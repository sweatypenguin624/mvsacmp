counter_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(counter_path, 'r') as f:
    counter_code = f.read()

# Fix the fragment merge loop
counter_code = counter_code.replace(
    "for rc_frame, rc_dir, rc_class, rc_bc in self.recent_crossings:",
    "for rc_frame, rc_dir, rc_class, rc_bc, rc_tid in self.recent_crossings:"
)

with open(counter_path, 'w') as f:
    f.write(counter_code)

print("Fixed the other loop.")
