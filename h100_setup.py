import yaml
from pathlib import Path
import os
import subprocess

config_dir = Path("vehicle-counting/config")

for yaml_file in config_dir.glob("vehicle_count_config_cvc*.yaml"):
    with open(yaml_file, "r") as f:
        cfg = yaml.safe_load(f)
        
    if "model" not in cfg:
        cfg["model"] = {}
        
    # Set to H100 engine for ALL cameras
    cfg["model"]["yolo_weights"] = "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X_h100.engine"
    
    with open(yaml_file, "w") as f:
        yaml.dump(cfg, f, sort_keys=False)

print("Updated YAML configs for H100.")

# Now update the bash script to assign all cameras to GPU 0
bash_script_path = "run_11_cvc_cameras.sh"
with open(bash_script_path, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("start_cam"):
        # Replace the 4th argument (GPU index) with 0
        # e.g. start_cam "cam_cvc3_cam_1" "1AQx8un5dlHqAuzYgFU431NrVffifrEhJ" "cvc3_cam_1" "2"
        parts = line.split('"')
        if len(parts) >= 9:
            parts[-2] = "0"  # The GPU index is the last quoted argument
        new_lines.append('"'.join(parts))
    else:
        new_lines.append(line)

with open(bash_script_path, "w") as f:
    f.writelines(new_lines)

print("Updated run_11_cvc_cameras.sh for H100.")

subprocess.run("pkill -9 -f main.py", shell=True)
subprocess.run("pkill -9 -f orchestrator.py", shell=True)
subprocess.run("tmux kill-server", shell=True)

print("Clean restart...")
subprocess.run("./run_11_cvc_cameras.sh", shell=True)
