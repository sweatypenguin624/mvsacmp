import yaml
import glob
valid = []
invalid = []
for f in sorted(glob.glob("vehicle_count_config_cvc*.yaml")):
    try:
        with open(f) as file:
            data = yaml.safe_load(file)
            line = data.get("roi", {}).get("counting_line", [])
            if not line or line == [[0, 0], [0, 0]] or line == [[0.0, 0.0], [0.0, 0.0]]:
                invalid.append(f)
            else:
                valid.append(f)
    except Exception as e:
        pass
print("VALID:")
for v in valid: print(" -", v)
print("INVALID:")
for i in invalid: print(" -", i)
