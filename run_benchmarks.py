import yaml
import subprocess
import re
import sys
import time
from pathlib import Path

config_path = Path("/home/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config.yaml")

def set_config(tracker, fps, with_reid):
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    cfg['model']['tracker'] = f"{tracker}.yaml"
    cfg['processing']['processing_fps'] = fps
    cfg['processing']['max_duration_minutes'] = 2
    if 'tracker' not in cfg:
        cfg['tracker'] = {}
    cfg['tracker']['with_reid'] = with_reid
    if with_reid:
        cfg['tracker']['reid_model'] = "osnet_x0_25_msmt17.pt"
    else:
        cfg['tracker']['reid_model'] = "auto"
    
    with open(config_path, 'w') as f:
        yaml.dump(cfg, f)

runs = [
    ("ByteTrack + FPS Skip", "bytetrack", 30, False),
    ("BoT-SORT + FPS Skip", "botsort", 30, False),
    ("ByteTrack + Native FPS", "bytetrack", 0, False),
    ("BoT-SORT + Native FPS", "botsort", 0, False),
    ("BoT-SORT + Re-ID", "botsort", 0, True)
]

results = []

for name, tracker, fps, reid in runs:
    print(f"Running {name}...")
    set_config(tracker, fps, reid)
    
    start_time = time.time()
    
    with open("run_temp.log", "w") as out_file:
        proc = subprocess.run([
            "/home/users/oauser/mvsa/env/bin/python",
            "vehicle-counting/pipeline/counting/main.py",
            "--video", "/home/users/oauser/mvsa/realrun/test.mp4"
        ], stdout=out_file, stderr=subprocess.STDOUT)
    
    with open("run_temp.log", "r") as f:
        out = f.read()
        
    counted = len(re.findall(r"COUNTED track_id=", out))
    rejections = len(re.findall(r"SAFETY NET REJECTION", out))
    merges = len(re.findall(r"SAFETY NET MERGE", out))
    
    results.append({
        "Name": name,
        "Counts": counted,
        "Rejections": rejections,
        "Merges": merges,
        "Time(s)": int(time.time() - start_time)
    })
    
print("\n--- BENCHMARK RESULTS ---")
print(f"{'Test':<25} | {'Count':<6} | {'Rejections':<10} | {'Merges':<6} | {'Time(s)'}")
print("-" * 65)
for r in results:
    print(f"{r['Name']:<25} | {r['Counts']:<6} | {r['Rejections']:<10} | {r['Merges']:<6} | {r['Time(s)']}")
