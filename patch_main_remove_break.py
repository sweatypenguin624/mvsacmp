import sys

file_path = '/home/users/oauser/mvsa/scripts/vehicle_counting/Vclassification/main.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "if total_frames >= 200:" in line or "logger.info(\"Stopping at 200 frames for performance testing.\")" in line or "break" in line and "Stopping at" in lines[lines.index(line)-1]:
        pass
    else:
        new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)
