import yaml
import subprocess
import re
import sys
import time
from pathlib import Path

config_path = Path("/home/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config.yaml")

def set_config():
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    cfg['model']['tracker'] = "botsort.yaml"
    cfg['processing']['processing_fps'] = 0
    if 'tracker' not in cfg:
        cfg['tracker'] = {}
    cfg['tracker']['with_reid'] = True
    cfg['tracker']['reid_model'] = "osnet_x0_25_msmt17.pt"
    
    with open(config_path, 'w') as f:
        yaml.dump(cfg, f)

print(f"Running BoT-SORT + Re-ID...")
set_config()

start_time = time.time()

with open("run_temp_reid.log", "w") as out_file:
    proc = subprocess.run([
        "/home/users/oauser/mvsa/env/bin/python",
        "vehicle-counting/pipeline/counting/main.py",
        "--video", "/home/users/oauser/mvsa/realrun/test.mp4"
    ], stdout=out_file, stderr=subprocess.STDOUT)

with open("run_temp_reid.log", "r") as f:
    out = f.read()
    
counted = len(re.findall(r"COUNTED track_id=", out))
rejections = len(re.findall(r"SAFETY NET REJECTION", out))
merges = len(re.findall(r"SAFETY NET MERGE", out))

print("\n--- BENCHMARK RESULTS ---")
print(f"Test: BoT-SORT + Re-ID")
print(f"Count: {counted}")
print(f"Rejections: {rejections}")
print(f"Merges: {merges}")
print(f"Time: {int(time.time() - start_time)}s")
