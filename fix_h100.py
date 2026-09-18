import os
import glob

files = glob.glob("/storage/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config_cvc*.yaml")
for f in files:
    with open(f, "r") as file:
        content = file.read()
    content = content.replace("UVH-26-MV-YOLOv11-X_a100.engine", "UVH-26-MV-YOLOv11-X_h100.engine")
    content = content.replace("UVH-26-MV-YOLOv11-X.pt", "UVH-26-MV-YOLOv11-X_h100.engine")
    with open(f, "w") as file:
        file.write(content)
print(f"Updated {len(files)} YAML configs to use H100 engine.")
