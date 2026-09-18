import re

with open("/home/users/oauser/mvsa/report_data.txt", "r") as f:
    lines = f.readlines()

output = "# Vehicle Crossing Validation Report (Original Baseline)\n\n"
output += "This report summarizes the crossing events and deduplication rejections extracted from the previous full run on `test.mp4`.\n\n"
output += "## Crossings & Rejections\n"
output += "| Frame | Event Type | Track ID | Class | Details (Reason / Prev Track ID / Distance) |\n"
output += "|---|---|---|---|---|\n"

for line in lines:
    if "COUNTED" in line:
        m = re.search(r"frame=(\d+) COUNTED track_id=(\d+) class=(.*)", line)
        if m:
            frame, tid, cls = m.groups()
            output += f"| {frame} | 🟢 COUNTED | {tid} | {cls} | - |\n"
    elif "REJECT" in line:
        # e.g. 2026-08-29 09:36:54 [INFO] uvh_test.counter: SAFETY NET REJECTION: Rejecting tid=5 as duplicate of class Truck, prev_tid=4, dist=72.3px, thresh=300.0px, bbox_size=458.9x384.3
        m = re.search(r"Rejecting tid=(\d+) as duplicate of class (.*?), prev_tid=(\d+), dist=(.*?), thresh", line)
        if m:
            tid, cls, prev_tid, dist = m.groups()
            output += f"| ~ | 🔴 REJECTED | {tid} | {cls} | Fragment of {prev_tid} (dist={dist}) |\n"

with open("/home/users/oauser/.gemini/antigravity-ide/brain/6a8f6e9c-dfa6-4d13-b073-52672c549073/validation_report.md", "w") as f:
    f.write(output)
print("Artifact created")
