import json

line_y = 842  # Approximate y-coordinate of the counting line

with open('/home/users/oauser/mvsa/results/vehicle_count_v1/tracks.jsonl', 'r') as f:
    tracks = [json.loads(line) for line in f]

for t in tracks:
    tid = t["track_id"]
    if tid in [2, 3, 4, 10, 13, 15, 25, 29, 30]:
        cbox = t["creation_bbox"]
        c_y2 = cbox[3]
        lbox = t.get("last_bbox", cbox) # might not have last_bbox in jsonl
        # let's just print what we have
        print(f"Track {tid}: {t['class']} frames {t['first_frame']}-{t['last_frame']} (life {t['lifespan']}) max_lost {t['max_lost_gap']}")
        print(f"  creation_bbox: y2={c_y2:.1f} (dist to line: {c_y2 - line_y:.1f})")
        print(f"  crossed: {t['crossed']} reason: {t['not_counted_reason']}")
