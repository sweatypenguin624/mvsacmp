import yaml
from pathlib import Path
import os
import subprocess

config_dir = Path("vehicle-counting/config")

# GPU 2 (A100) runs cvc8, cvc9, cvc10. So ONLY these get the a100 engine!
a100_cams = {"cvc8_cam_1", "cvc9_cam_1", "cvc10_cam_1"}

for yaml_file in config_dir.glob("vehicle_count_config_cvc*.yaml"):
    cam_name = yaml_file.stem.replace("vehicle_count_config_", "")
    
    with open(yaml_file, "r") as f:
        cfg = yaml.safe_load(f)
        
    if "model" not in cfg:
        cfg["model"] = {}
        
    if cam_name in a100_cams:
        cfg["model"]["yolo_weights"] = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X_a100.engine"
    else:
        cfg["model"]["yolo_weights"] = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X.pt"
        
    with open(yaml_file, "w") as f:
        yaml.dump(cfg, f, sort_keys=False)
        
print("Configs correctly patched.")

# Completely wipe existing orchestrator & main.py processes to avoid zombie leaks
subprocess.run("pkill -9 -f main.py", shell=True)
subprocess.run("pkill -9 -f orchestrator.py", shell=True)
subprocess.run("tmux kill-server", shell=True)

# Relaunch
print("Clean restart...")
subprocess.run("./run_11_cvc_cameras.sh", shell=True)
