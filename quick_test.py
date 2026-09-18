import subprocess
import re

def run_test():
    proc = subprocess.run([
        "/home/users/oauser/mvsa/env/bin/python",
        "vehicle-counting/pipeline/counting/main.py",
        "--video", "/home/users/oauser/mvsa/realrun/test.mp4"
    ], capture_output=True, text=True)
    out = proc.stderr + proc.stdout
    c = len(re.findall(r"COUNTED track_id=", out))
    r = len(re.findall(r"SAFETY NET REJECTION", out))
    m = len(re.findall(r"SAFETY NET MERGE", out))
    return c, r, m

# 1. Run with NEW patched logic
print("Testing patched logic (Spanning + Proximity)...")
c1, r1, m1 = run_test()

# 2. Revert to strict segment logic
subprocess.run(["cp", "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py.bak2", "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"])

print("Testing strict segment logic...")
c2, r2, m2 = run_test()

# 3. Restore patched logic
subprocess.run(["cp", "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py.bak", "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"]) # Wait, bak2 was the strict one. Let me re-run patch_counter.py
subprocess.run(["python3", "/home/users/oauser/mvsa/patch_counter.py"])

print(f"\n--- COMPARISON ---")
print(f"Patched (Spanning): Counts={c1}, Rejections={r1}, Merges={m1}")
print(f"Original (Strict Segment): Counts={c2}, Rejections={r2}, Merges={m2}")
