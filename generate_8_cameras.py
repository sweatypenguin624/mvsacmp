import os
import subprocess
import json

OUT_DIR = "/home/users/oauser/mvsa/vehicle-count-output"
os.makedirs(OUT_DIR, exist_ok=True)

roots = {
    "cvc3": "1471o4gcuNTUerIRm7QIj6nvCFwXWhwyk",
    "cvc4": "1u5oo6FfzkXSObybW12teSH9u2nTPWQwC",
    "cvc5": "1ekMGsormVsfO9NO3o9Us5-Q6cx1297HX",
    "cvc6": "1RaF2p92Rirj5CwnVgqH3e2A0VHihr-Iv",
    "cvc7": "1K3k8RXDAvcSD4vuuXbL_jWwXivphORb6",
    "cvc8": "1yOdHYE3EFZimAslSZx99zIhdDZ3WSrJp",
    "cvc9": "1bggk1ddkr5QyXQZS0sHUY-lbv9WuFaG6",
    "cvc10": "1rg5Jpt0Reane34A97YehEfJGvOBr2X8S"
}

RCLONE = "tools/rclone-v1.75.0-linux-amd64/rclone"
FFMPEG = "tools/ffmpeg_bin/ffmpeg"

cameras_to_run = []

for loc, f_id in roots.items():
    print(f"Scanning {loc}...")
    cmd = [RCLONE, "--config", "config/rclone.conf", "lsjson", "--max-depth", "1", f"Gdrive-yogesh,root_folder_id={f_id}:"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        dirs = json.loads(res.stdout)
    except:
        continue
        
    for d in dirs:
        if d.get("IsDir") and "backup" not in d.get("Name", "").lower():
            cam_id = d["ID"]
            cam_name = d["Name"].replace(" ", "_").replace("-", "")
            final_name = f"{loc}_{cam_name}"
            cameras_to_run.append((final_name, cam_id))
            
            # extract frame
            print(f"Extracting frame for {final_name} into vehicle-count-output/")
            remote = f"Gdrive-yogesh,root_folder_id={cam_id}:"
            # find dav
            c2 = [RCLONE, "--config", "config/rclone.conf", "lsjson", "-R", "--files-only", remote]
            r2 = subprocess.run(c2, capture_output=True, text=True)
            try:
                files = json.loads(r2.stdout)
            except:
                continue
                
            dav_file = None
            for f in files:
                if f.get("Name", "").endswith(".dav"):
                    dav_file = f["Path"]
                    break
            
            if dav_file:
                out_img = os.path.join(OUT_DIR, f"{final_name}_frame.jpg")
                p1 = subprocess.Popen([RCLONE, "--config", "config/rclone.conf", "cat", f"{remote}{dav_file}"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                p2 = subprocess.Popen([FFMPEG, "-y", "-i", "pipe:0", "-vframes", "1", "-q:v", "2", out_img], stdin=p1.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                p1.stdout.close()
                p2.communicate()
            
            # create config
            model_weight = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X_a100.engine"
            if len(cameras_to_run) > 4:  # put first 4 on A100, next on V100/P100 (which need .pt)
                model_weight = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X.pt"
            
            config_content = f"""model:
  confidence: 0.35
  device: cuda:0
  imgsz: 640
  tracker: bytetrack.yaml
  yolo_weights: {model_weight}
roi:
  count_direction: BOTH
  counting_line:
  - - 0
    - 0
  - - 0
    - 0
  reference_height: 1080
  reference_width: 1920
disable_subclassifiers: true
"""
            with open(f"vehicle-counting/config/vehicle_count_config_{final_name}.yaml", "w") as f:
                f.write(config_content)
            
            if len(cameras_to_run) == 8:
                break
    if len(cameras_to_run) == 8:
        break

print("Creating bash script run_8_cvc_cameras.sh...")
bash_script = """#!/bin/bash
set -e
cd /home/users/oauser/mvsa

start_cam() {
    local SESSION_NAME="$1"
    local FOLDER_ID="$2"
    local CAM_NAME="$3"
    local DEVICE="$4"
    local DB_PATH="historical-processor/data/manifest_${CAM_NAME}.db"
    local OUT_DIR="historical-processor/output/${CAM_NAME}"
    local CFG_PATH="vehicle-counting/config/vehicle_count_config_${CAM_NAME}.yaml"

    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux kill-session -t "$SESSION_NAME"
    fi

    echo "Launching $CAM_NAME on GPU $DEVICE"
    tmux new-session -d -s "$SESSION_NAME" \\
        "export CUDA_VISIBLE_DEVICES=$DEVICE && env/bin/python historical-processor/orchestrator.py \\
            --folder-id '$FOLDER_ID' \\
            --camera-name '$CAM_NAME' \\
            --db '$DB_PATH' \\
            --output-dir '$OUT_DIR' \\
            --config '$CFG_PATH' \\
            --dl-threads 16 \\
            --inf-threads 4 \\
            --scan"
}

"""
for i, (cam_name, cam_id) in enumerate(cameras_to_run):
    if i < 4: device = 0
    elif i < 6: device = 1
    else: device = 2
    bash_script += f"start_cam \"cam_{cam_name}\" \"{cam_id}\" \"{cam_name}\" \"{device}\"\n"

bash_script += "echo \"All 8 cameras launched!\"\n"
with open("run_8_cvc_cameras.sh", "w") as f:
    f.write(bash_script)
os.chmod("run_8_cvc_cameras.sh", 0o755)
print("Done!")
