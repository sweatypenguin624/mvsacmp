counter_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(counter_path, 'r') as f:
    counter_code = f.read()

# The current block to replace:
#                             if dist < 150:
#                                 logger.info(f"SAFETY NET REJECTION: Rejecting tid={tid} as duplicate of class {stable_class}, prev_tid={rc_tid}, dist={dist:.1f}px, bbox_size={box[2]-box[0]:.1f}x{box[3]-box[1]:.1f}")
#                                 is_duplicate = True
#                                 break

new_logic = """
                            box_width = box[2] - box[0]
                            if stable_class == "Bus":
                                thresh = min(350, max(150, box_width * 0.75))
                            elif stable_class in ["Truck", "tempo-traveller"]:
                                thresh = min(300, max(150, box_width * 0.75))
                            else:
                                thresh = 150
                            
                            if dist < thresh:
                                logger.info(f"SAFETY NET REJECTION: Rejecting tid={tid} as duplicate of class {stable_class}, prev_tid={rc_tid}, dist={dist:.1f}px, thresh={thresh:.1f}px, bbox_size={box_width:.1f}x{box[3]-box[1]:.1f}")
                                is_duplicate = True
                                break"""

import re
counter_code = re.sub(
    r"\s*if dist < 150:\n\s*logger\.info\(f\"SAFETY NET REJECTION: Rejecting tid=\{tid\} as duplicate of class \{stable_class\}, prev_tid=\{rc_tid\}, dist=\{dist:\.1f\}px, bbox_size=\{box\[2\]-box\[0\]:\.1f\}x\{box\[3\]-box\[1\]:\.1f\}\"\)\n\s*is_duplicate = True\n\s*break",
    new_logic,
    counter_code
)

with open(counter_path, 'w') as f:
    f.write(counter_code)

print("Dynamic threshold patched.")
