import os
import shutil

counter_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"
output_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/output.py"
main_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/main.py"

shutil.copy(counter_path, counter_path + ".bak4")
shutil.copy(output_path, output_path + ".bak")
shutil.copy(main_path, main_path + ".bak2")

# 1. Update counter.py
with open(counter_path, 'r') as f:
    counter_code = f.read()

# Current loop logic replacement
counter_code = counter_code.replace(
    "[(f, d, c, bc) for f, d, c, bc in self.recent_crossings if self.frame_count - f < 150]",
    "[(f, d, c, bc, t) for f, d, c, bc, t in self.recent_crossings if self.frame_count - f < 150]"
)

counter_code = counter_code.replace(
    "for f, d, c, bc in self.recent_crossings:",
    "for f, d, c, bc, t in self.recent_crossings:"
)

old_log = 'logger.info(f"SAFETY NET REJECTION: Rejecting tid={tid} as duplicate of class {stable_class}, dist={dist:.1f}px")'
new_log = 'logger.info(f"SAFETY NET REJECTION: Rejecting tid={tid} as duplicate of class {stable_class}, prev_tid={t}, dist={dist:.1f}px, bbox_size={box[2]-box[0]:.1f}x{box[3]-box[1]:.1f}")'
counter_code = counter_code.replace(old_log, new_log)

old_append = "self.recent_crossings.append((self.frame_count, dir_str, stable_class, curr_bc))"
new_append = "self.recent_crossings.append((self.frame_count, dir_str, stable_class, curr_bc, tid))"
counter_code = counter_code.replace(old_append, new_append)

with open(counter_path, 'w') as f:
    f.write(counter_code)


# 2. Update output.py
with open(output_path, 'r') as f:
    output_code = f.read()

old_draw = 'def draw_track(self, frame, box, tid, cls_name, conf, counted, state_str="NEW"):'
new_draw = 'def draw_track(self, frame, box, tid, cls_name, conf, counted, state_str="NEW", not_counted_reason=""):'
output_code = output_code.replace(old_draw, new_draw)

old_color = 'color = (0, 255, 0) if counted else (255, 0, 0)'
new_color = 'color = (0, 255, 255) if counted and not_counted_reason == "Duplicate" else ((0, 255, 0) if counted else (255, 0, 0))'
output_code = output_code.replace(old_color, new_color)

with open(output_path, 'w') as f:
    f.write(output_code)


# 3. Update main.py
with open(main_path, 'r') as f:
    main_code = f.read()

old_main_draw = 'annotator.draw_track(frame, box, tid, stable_class, conf, state.counted, state_str=state.state.value)'
new_main_draw = 'annotator.draw_track(frame, box, tid, stable_class, conf, state.counted, state_str=state.state.value, not_counted_reason=getattr(state, "not_counted_reason", ""))'
main_code = main_code.replace(old_main_draw, new_main_draw)

old_bottom = 'annotator.write_frame(frame)'
new_bottom = """
                total_count = sum(counter.counts_by_class.values())
                h, w = frame.shape[:2]
                cv2.putText(frame, f"TOTAL: {total_count}", (w - 300, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                annotator.write_frame(frame)"""
main_code = main_code.replace(old_bottom, new_bottom)

with open(main_path, 'w') as f:
    f.write(main_code)

print("Patch applied successfully.")
