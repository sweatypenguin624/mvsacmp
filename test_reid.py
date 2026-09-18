import yaml
import subprocess
import re

config_path = "/home/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config.yaml"
with open(config_path, 'r') as f:
    cfg = yaml.safe_load(f)

cfg['model']['tracker'] = "botsort.yaml"
if 'tracker' not in cfg:
    cfg['tracker'] = {}
cfg['tracker']['with_reid'] = True
cfg['tracker']['reid_model'] = "yolo26n-reid.onnx"
cfg['tracker']['min_track_frames'] = 3
cfg['tracker']['match_thresh'] = 0.8
cfg['tracker']['new_track_thresh'] = 0.5
cfg['tracker']['track_buffer'] = 120

with open(config_path, 'w') as f:
    yaml.dump(cfg, f)

proc = subprocess.run([
    "/home/users/oauser/mvsa/env/bin/python",
    "vehicle-counting/pipeline/counting/main.py",
    "--video", "/home/users/oauser/mvsa/realrun/test.mp4"
], capture_output=True, text=True)

out = proc.stderr + proc.stdout
c = len(re.findall(r"COUNTED track_id=", out))
r = len(re.findall(r"SAFETY NET REJECTION", out))
m = len(re.findall(r"SAFETY NET MERGE", out))
print(f"BoT-SORT + ReID (yolo26n-reid.onnx): Counts={c}, Rejections={r}, Merges={m}")
