import subprocess
import json
import re
import os
import yaml

def parse_camera_name(path):
    parts = path.split('/')
    if len(parts) < 2: return None
    
    m1 = re.search(r'CVC\s*(\d+)', parts[0], re.IGNORECASE)
    if not m1: return None
    cvc_num = m1.group(1)
    
    cam_part = parts[1]
    m2 = re.search(r'Cam\s*(\d+)', cam_part, re.IGNORECASE)
    if not m2: return None
    cam_num = m2.group(1)
    
    suffix = ""
    m3 = re.search(r'\b(EB|WB|NB|SB|IR)\b', cam_part, re.IGNORECASE)
    if m3:
        suffix = "__" + m3.group(1).lower()
        
    return f"cvc{cvc_num}_cam_{cam_num}{suffix}"

def is_valid_config(yaml_path):
    if not os.path.exists(yaml_path):
        return False
    try:
        with open(yaml_path) as file:
            data = yaml.safe_load(file)
            line = data.get("roi", {}).get("counting_line", [])
            if not line or line == [[0, 0], [0, 0]] or line == [[0.0, 0.0], [0.0, 0.0]]:
                return False
            return True
    except Exception:
        return False

def main():
    root_folder_id = "18Og7JJ_PzwEMHYyj-rb_VTiUKYMkU9_k"
    cmd = ["tools/rclone-v1.75.0-linux-amd64/rclone", "lsjson", f"abhaydrive,root_folder_id={root_folder_id}:", "--max-depth", "2", "--fast-list"]
    print("Fetching subfolders from Google Drive...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error running rclone:", result.stderr)
        return
        
    files = json.loads(result.stdout)
    folders = [f for f in files if f.get('IsDir', False) and '/' in f.get('Path', '')]
    
    valid_cameras = []
    
    for folder in folders:
        path = folder['Path']
        folder_id = folder['ID']
        cam_name = parse_camera_name(path)
        if not cam_name:
            continue
            
        yaml_path = f"vehicle-counting/config/vehicle_count_config_{cam_name}.yaml"
        if is_valid_config(yaml_path):
            valid_cameras.append((cam_name, folder_id, path))
            
    print(f"Found {len(valid_cameras)} valid camera configurations matching Drive subfolders:")
    for cam_name, folder_id, path in valid_cameras:
        print(f" - {cam_name} (Drive Path: {path})")
        
    for i, (cam_name, folder_id, path) in enumerate(valid_cameras):
        session_name = f"cam_{cam_name}"
        db_path = f"historical-processor/data/manifest_{cam_name}.db"
        cfg_path = f"vehicle-counting/config/vehicle_count_config_{cam_name}.yaml"
        
        # Kill existing tmux session if any
        subprocess.run(["tmux", "kill-session", "-t", session_name], stderr=subprocess.DEVNULL)
        
        device = "0"
        
        tmux_cmd = (
            f"bash -c \"export CUDA_DEVICE_ORDER=PCI_BUS_ID && export CUDA_VISIBLE_DEVICES={device} && "
            f".venv/bin/python historical-processor/orchestrator.py "
            f"--folder-id '{folder_id}' "
            f"--camera-name '{cam_name}' "
            f"--db '{db_path}' "
            f"--config '{cfg_path}' "
            f"--ephemeral-dir '/ephemeral/mvsacmp' "
            f"--dl-threads 1 "
            f"--inf-threads 4 "
            f"--max-concurrent-inference 15 "
            f"--no-dali "
            f"--scan\""
        )
        print(f"\nLaunching {cam_name} in tmux...")
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name, tmux_cmd])
        
    print("\nAll valid MP4 cameras launched successfully!")

if __name__ == "__main__":
    main()
