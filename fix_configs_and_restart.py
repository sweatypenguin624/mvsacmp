import yaml
from pathlib import Path
import os
import subprocess

config_dir = Path("vehicle-counting/config")

a100_cams = {"cvc3_cam_1", "cvc4_cam_1", "cvc5_cam_1__ir", "cvc5_cam_2"}

for yaml_file in config_dir.glob("vehicle_count_config_cvc*.yaml"):
    cam_name = yaml_file.stem.replace("vehicle_count_config_", "")
    
    with open(yaml_file, "r") as f:
        cfg = yaml.safe_load(f)
        
    cfg["disable_subclassifiers"] = True
    
    if "model" not in cfg:
        cfg["model"] = {}
        
    if cam_name in a100_cams:
        cfg["model"]["yolo_weights"] = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X_a100.engine"
    else:
        cfg["model"]["yolo_weights"] = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X.pt"
        
    with open(yaml_file, "w") as f:
        yaml.dump(cfg, f, sort_keys=False)
        
print("Configs patched.")

# Kill existing tmux sessions
subprocess.run("tmux ls | grep cam_ | cut -d: -f1 | xargs -I {} tmux kill-session -t {}", shell=True, capture_output=True)

# Relaunch
print("Restarting cameras...")
subprocess.run("./run_11_cvc_cameras.sh", shell=True)
