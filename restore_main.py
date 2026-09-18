import re

file_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/main.py"

with open(file_path, "r") as f:
    content = f.read()

content = content.replace("for frame_idx, frame in reader.frames(start_frame=25000):", "for frame_idx, frame in reader.frames(start_frame=0):")

content = content.replace("if frame_idx > 25700:", "if max_duration_minutes > 0 and (total_frames / fps) >= (max_duration_minutes * 60):")

with open(file_path, "w") as f:
    f.write(content)
