import sys
import os
from pathlib import Path
import subprocess
import time
import queue
import threading
import argparse
import fcntl
import shutil

# Ensure historical-processor is on sys.path
HIST_DIR = Path(__file__).resolve().parent
if str(HIST_DIR) not in sys.path:
    sys.path.insert(0, str(HIST_DIR))

# Always use project virtual environment python if it exists
ENV_PYTHON = "/home/users/oauser/mvsa/env/bin/python"
if not os.path.exists(ENV_PYTHON):
    ENV_PYTHON = sys.executable

from ingest.manifest import IngestManifest
from ingest.downloader import Downloader
from ingest.drive_scanner import DriveScanner

def run_command(cmd, desc):
    print(f"\n[{threading.current_thread().name}] --- {desc} ---")
    print(f"[{threading.current_thread().name}] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[{threading.current_thread().name}] ERROR in {desc}:\n{result.stderr}")
    return result.returncode == 0

# Cross-process GPU concurrency cap. Each camera runs in its own tmux
# session/process with its own --inf-threads, so per-process thread limits
# don't stop multiple cameras from hammering the same physical GPU at once.
# These slot lock files are shared (by path) across every orchestrator
# process on the box, so together they cap TOTAL concurrent inference
# subprocesses regardless of how many cameras are running.
def acquire_gpu_slot(slots_dir, num_slots):
    os.makedirs(slots_dir, exist_ok=True)
    # Artificially cap concurrency to 5 so we process in smaller, faster batches
    actual_slots = min(num_slots, 5)
    while True:
        for i in range(actual_slots):
            slot_path = os.path.join(slots_dir, f"slot_{i}.lock")
            fh = open(slot_path, "w")
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fh
            except BlockingIOError:
                fh.close()
        time.sleep(2)

def release_gpu_slot(fh):
    fcntl.flock(fh, fcntl.LOCK_UN)
    fh.close()

def download_and_remux_worker(download_queue, inference_queue, manifest, folder_id, base_dir):
    downloader = Downloader(root_folder_id=folder_id)
    
    while True:
        item = download_queue.get()
        if item is None:
            break
            
        file_id = item['file_id']
        gdrive_path = item['gdrive_path']
        date = item['date']
        filename = item['filename']
        timestamp = filename.replace('.dav', '').replace('.mp4', '')
        
        local_dir = os.path.join(base_dir, date)
        local_file = os.path.join(local_dir, filename)
        local_mp4 = local_file if filename.endswith('.mp4') else local_file + ".mp4"
        
        # 1. Download
        manifest.update_status(file_id, "DOWNLOADING")
        print(f"[{threading.current_thread().name}] Downloading {filename} to {local_file}")
        if not downloader.download_file(gdrive_path, local_file):
            manifest.update_status(file_id, "FAILED", error="Download failed")
            download_queue.task_done()
            continue
            
        # 2. Remux
        manifest.update_status(file_id, "DOWNLOADED", local_path=local_file)
        if filename.endswith('.dav'):
            remux_cmd = ['ffmpeg', '-y', '-i', local_file, '-c', 'copy', local_mp4]
            if not run_command(remux_cmd, f"Remuxing {filename}"):
                manifest.update_status(file_id, "FAILED", error="Remux failed")
                download_queue.task_done()
                continue
            
        # 3. Pass to inference
        item['local_dav'] = local_file
        item['local_mp4'] = local_mp4
        item['timestamp'] = timestamp
        inference_queue.put(item)
        download_queue.task_done()

def inference_worker(inference_queue, manifest, base_output_dir, folder_id, config_file=None,
                      gpu_slots_dir=None, max_concurrent_inference=1, use_dali=True, ephemeral_dir=None):
    while True:
        item = inference_queue.get()
        if item is None:
            break

        file_id = item['file_id']
        date = item['date']
        filename = item['filename']
        timestamp = item['timestamp']
        local_dav = item['local_dav']
        local_mp4 = item['local_mp4']

        start_time_part = timestamp.split('-')[0]
        start_time_formatted = start_time_part.replace('.', ':')

        output_dir = os.path.join(base_output_dir, date, timestamp)
        os.makedirs(output_dir, exist_ok=True)

        # Inference using verified env python
        inference_cmd = [
            ENV_PYTHON, 'vehicle-counting/pipeline/counting/main.py',
            '--video', local_mp4,
            '--output_dir', output_dir,
            '--no_annotation',
            '--start_time', start_time_formatted
        ]
        if config_file:
            inference_cmd.extend(['--config', config_file])
        if use_dali:
            inference_cmd.append('--use_dali')

        # Block here (not while holding the GPU) until a slot is free, so we
        # never run more than max_concurrent_inference inference subprocesses
        # -- across ALL cameras on this box -- against the GPU at once.
        slot = acquire_gpu_slot(gpu_slots_dir, max_concurrent_inference)
        try:
            success = run_command(inference_cmd, f"Inference {filename}")
        finally:
            release_gpu_slot(slot)

        if not success:
            manifest.update_status(file_id, "FAILED", error="Inference failed")
        else:
            manifest.update_status(file_id, "COMPLETED")
            print(f"\n[{threading.current_thread().name}] SUCCESS: Completed {filename}")
            
            # Upload results back to Google Drive
            print(f"[{threading.current_thread().name}] Uploading results to Google Drive...")
            gdrive_dest = f"abhaydrive,root_folder_id={folder_id}:results/{date}/{timestamp}"
            upload_cmd = [
                'tools/rclone-v1.75.0-linux-amd64/rclone',
                'copy', output_dir, gdrive_dest
            ]
            if not run_command(upload_cmd, f"Uploading {filename} results"):
                print(f"[{threading.current_thread().name}] WARNING: Failed to upload results to {gdrive_dest}")
            
            # Cleanup only on success to prevent storage growth
            print(f"[{threading.current_thread().name}] Deleting local video files for {filename}")
            if os.path.exists(local_dav):
                try:
                    os.remove(local_dav)
                except OSError as e:
                    print(f"[{threading.current_thread().name}] WARNING: Failed to delete {local_dav}: {e}")
            if local_mp4 != local_dav and os.path.exists(local_mp4):
                try:
                    os.remove(local_mp4)
                except OSError as e:
                    print(f"[{threading.current_thread().name}] WARNING: Failed to delete {local_mp4}: {e}")
                    
        if ephemeral_dir:
            try:
                usage = shutil.disk_usage(ephemeral_dir)
                free_gb = usage.free / (1024**3)
                print(f"[{threading.current_thread().name}] Ephemeral disk free space: {free_gb:.1f} GB")
            except Exception as e:
                print(f"[{threading.current_thread().name}] Could not check disk space: {e}")
            
        inference_queue.task_done()

def main():
    parser = argparse.ArgumentParser(description="Multi-threaded Orchestrator for Historical Video Processing")
    parser.add_argument('--folder-id', type=str, required=True, help="Google Drive folder ID")
    parser.add_argument('--camera-name', type=str, default=None, help="Camera identifier (e.g. tvc5_wb)")
    parser.add_argument('--db', type=str, default=None, help="Manifest database path")
    parser.add_argument('--output-dir', type=str, default=None, help="Output directory for results")
    parser.add_argument('--config', type=str, default=None, help="Vehicle count config YAML path")
    parser.add_argument('--dl-threads', type=int, default=4, help="Number of download/remux threads")
    parser.add_argument('--inf-threads', type=int, default=2, help="Number of inference threads")
    parser.add_argument('--batch-size', type=int, default=5, help="Batch size for fetching pending videos")
    parser.add_argument('--scan', action='store_true', help="Scan Google Drive before starting")
    parser.add_argument('--max-concurrent-inference', type=int, default=5,
                         help="Max inference subprocesses running at once ACROSS ALL cameras sharing this GPU "
                              "(enforced via shared lock files, not just this process's --inf-threads). "
                              "Keep this in sync across every camera launched on the same box/GPU.")
    parser.add_argument('--gpu-slots-dir', type=str, default="historical-processor/data/gpu_slots",
                         help="Shared directory for the cross-process GPU concurrency lock files.")
    parser.add_argument('--no-dali', action='store_true',
                         help="Disable NVDEC hardware video decode (--use_dali is passed to main.py by default; "
                              "main.py falls back to CPU decode automatically if DALI isn't available).")
    parser.add_argument('--ephemeral-dir', type=str, default=os.environ.get('CVC_EPHEMERAL_DIR', '/ephemeral/mvsacmp'),
                         help="Base directory for ephemeral storage")
    args = parser.parse_args()

    # Validate ephemeral directory
    ephemeral_base = '/ephemeral'
    if not os.path.exists(ephemeral_base) and not os.path.ismount(ephemeral_base):
        print(f"ERROR: Ephemeral base path '{ephemeral_base}' is not available.")
        print("Aborting to prevent silently filling up the root filesystem.")
        sys.exit(1)

    camera_name = args.camera_name or args.folder_id
    db_path = args.db or f"historical-processor/data/manifest_{camera_name}.db"
    output_dir = args.output_dir or os.path.join(args.ephemeral_dir, "output", camera_name)
    video_base_dir = os.path.join(args.ephemeral_dir, "videos", camera_name)
    temp_dir = os.path.join(args.ephemeral_dir, "temp", camera_name)
    cache_dir = os.path.join(args.ephemeral_dir, "cache", camera_name)
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(video_base_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    
    manifest = IngestManifest(db_path=db_path)
    
    stats = manifest.get_stats()
    if args.scan or stats.get('TOTAL', 0) == 0:
        print(f"Scanning Google Drive folder ID: {args.folder_id} ...")
        scanner = DriveScanner(root_folder_id=args.folder_id)
        scanner.scan(manifest)
        stats = manifest.get_stats()
        print(f"Scan complete. Total files in manifest: {stats.get('TOTAL', 0)}")
        
    download_queue = queue.Queue(maxsize=2)
    inference_queue = queue.Queue(maxsize=2)
    
    # Start thread pools
    dl_threads = []
    for i in range(args.dl_threads):
        t = threading.Thread(
            target=download_and_remux_worker,
            args=(download_queue, inference_queue, manifest, args.folder_id, video_base_dir),
            name=f"DL-Worker-{i}"
        )
        t.daemon = True
        t.start()
        dl_threads.append(t)
        
    inf_threads = []
    for i in range(args.inf_threads):
        t = threading.Thread(
            target=inference_worker,
            args=(inference_queue, manifest, output_dir, args.folder_id, args.config),
            kwargs=dict(
                gpu_slots_dir=args.gpu_slots_dir,
                max_concurrent_inference=args.max_concurrent_inference,
                use_dali=not args.no_dali,
                ephemeral_dir=args.ephemeral_dir,
            ),
            name=f"INF-Worker-{i}"
        )
        t.daemon = True
        t.start()
        inf_threads.append(t)
        
    print(f"\n=======================================================")
    print(f"Starting Orchestrator for: {camera_name}")
    print(f"Python Binary:{ENV_PYTHON}")
    print(f"Folder ID:    {args.folder_id}")
    print(f"Manifest DB:  {db_path}")
    print(f"Output Dir:   {output_dir}")
    print(f"Ephemeral Dir:{args.ephemeral_dir}")
    print(f"Config:       {args.config or 'default'}")
    print(f"Workers:      {args.dl_threads} DL, {args.inf_threads} INF")
    print(f"GPU cap:      {args.max_concurrent_inference} concurrent inference job(s) across ALL cameras (slots: {args.gpu_slots_dir})")
    print(f"NVDEC:        {'disabled' if args.no_dali else 'enabled (falls back to CPU decode if unavailable)'}")
    print(f"=======================================================\n")
    
    # Reset any previously stuck or failed files on fresh launch
    for status in ["DOWNLOADING", "DOWNLOADED", "QUEUED", "FAILED"]:
        for item in manifest.get_by_status(status):
            manifest.update_status(item['file_id'], "DISCOVERED")
        
    last_log_time = 0
    while True:
        current_time = time.time()
        if current_time - last_log_time > 60:
            print(f"[Main] Queue depths - DL: {download_queue.qsize()}, INF: {inference_queue.qsize()}")
            last_log_time = current_time

        if download_queue.qsize() < 10:
            batch = manifest.get_pending_batch(batch_size=args.batch_size)
            if not batch:
                # download_queue/inference_queue.qsize() only reflects items
                # NOT yet picked up by a worker thread -- it hits 0 the moment
                # a worker calls .get(), well before that item's download,
                # remux, or inference actually finishes. Checking qsize()==0
                # here races with in-flight work and exits (killing the daemon
                # worker threads) while the last item(s) in a batch are still
                # being processed, silently losing them. The manifest DB is
                # the source of truth for whether work is actually done.
                stats = manifest.get_stats()
                in_flight = (stats.get('DISCOVERED', 0) + stats.get('QUEUED', 0)
                             + stats.get('DOWNLOADING', 0) + stats.get('DOWNLOADED', 0))
                if in_flight == 0:
                    print(f"\nAll files processed for {camera_name}! Pipeline complete.")
                    break
                else:
                    time.sleep(5)
                    continue

            for item in batch:
                manifest.update_status(item['file_id'], "QUEUED")
                download_queue.put(item)

        time.sleep(1)

if __name__ == '__main__':
    main()
