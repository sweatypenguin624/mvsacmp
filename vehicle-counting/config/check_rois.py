import yaml
import glob
from pathlib import Path

for f in sorted(glob.glob("vehicle_count_config_cvc*.yaml")):
    try:
        with open(f) as file:
            data = yaml.safe_load(file)
            line = data.get("roi", {}).get("counting_line", "Not found")
            print(f"{f}: {line}")
    except Exception as e:
        print(f"{f}: Error {e}")
