import subprocess
import yaml

config_path = "/home/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config.yaml"
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

cfg["processing"]["max_duration_minutes"] = 1
cfg["processing"]["processing_fps"] = 0
cfg["logging"]["level"] = "DEBUG"

with open(config_path, "w") as f:
    yaml.dump(cfg, f)

video = "/home/users/oauser/mvsa/realrun/test.mp4"
log_file = "/home/users/oauser/mvsa/eval2_run.log"
print("Running pipeline for 1 minute on test.mp4...")

with open(log_file, "w") as out:
    subprocess.run([
        "/home/users/oauser/mvsa/env/bin/python",
        "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/main.py",
        "--video", video
    ], stdout=out, stderr=subprocess.STDOUT)
