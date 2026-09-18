import yaml

config_path = "/home/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config.yaml"
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

cfg["processing"]["max_duration_minutes"] = 1

with open(config_path, "w") as f:
    yaml.dump(cfg, f)
