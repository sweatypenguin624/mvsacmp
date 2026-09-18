import re

file_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/main.py"

with open(file_path, "r") as f:
    content = f.read()

content = content.replace("for frame_idx, frame in reader.frames(start_frame=0):", "for frame_idx, frame in reader.frames(start_frame=25000):")

content = content.replace("if max_duration_minutes > 0 and (total_frames / fps) >= (max_duration_minutes * 60):", "if frame_idx > 25700:")

with open(file_path, "w") as f:
    f.write(content)
print("Successfully patched main.py for targeted run.")
