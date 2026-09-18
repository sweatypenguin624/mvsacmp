import os

target = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(target, "r") as f:
    content = f.read()

old_str = """            # --- Anti-Fragmentation (Conservative) ---
            # If a track of the same class crossed recently in the same direction, and is very close,
            # this might be the same physical vehicle with a broken Track ID.
            is_fragment = False
            for rc_frame, rc_dir, rc_class, rc_point in self.recent_crossings:
                if rc_class == stable_class and rc_dir == direction:
                    if frame_idx - rc_frame < 60: # within 2 seconds (assuming 30fps)
                        dist = ((point[0] - rc_point[0])**2 + (point[1] - rc_point[1])**2)**0.5
                        if dist < 400.0: # spatial threshold
                            is_fragment = True
                            self.stats["rejected_duplicate"] += 1
                            logger.info(f"REJECTED: frame={frame_idx} tid={tid} as fragment of recent crossing.")
                            break"""

new_str = """            # --- Anti-Fragmentation (Conservative) ---
            # If a track of the same class crossed recently in the same direction, and is very close both in time and space,
            # this might be the same physical vehicle with a broken Track ID.
            is_fragment = False
            for rc_frame, rc_dir, rc_class, rc_point in self.recent_crossings:
                if rc_class == stable_class and rc_dir == direction:
                    if frame_idx - rc_frame < 15:  # within 0.5 seconds (reduced from 2 seconds to avoid rejecting followers)
                        dist = ((point[0] - rc_point[0])**2 + (point[1] - rc_point[1])**2)**0.5
                        bbox_size = max(box[2] - box[0], box[3] - box[1])
                        if dist < bbox_size:  # spatial threshold based on object size
                            is_fragment = True
                            self.stats["rejected_duplicate"] += 1
                            logger.info(f"REJECTED: frame={frame_idx} tid={tid} as fragment of recent crossing (dist={dist:.1f}, bbox_max={bbox_size:.1f}).")
                            break"""

content = content.replace(old_str, new_str)

real_path = os.path.realpath(target)
os.remove(target)
with open(target, "w") as f:
    f.write(content)
print("Patched!")
