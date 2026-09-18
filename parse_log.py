import re

with open("/home/users/oauser/mvsa/eval_run.log", "r") as f:
    logs = f.readlines()

counts = []
rejections = []

for line in logs:
    if "COUNT:" in line:
        counts.append(line.strip())
    elif "REJECTED:" in line:
        rejections.append(line.strip())

print("\n--- REPORT ---")
print(f"Total Valid Counts: {len(counts)}")
print(f"Total Rejections (Fragmentation): {len(rejections)}")

print("\n--- REJECTION LOGS ---")
for r in rejections:
    print(r)

print("\n--- ALL COUNTS ---")
for c in counts:
    print(c)
