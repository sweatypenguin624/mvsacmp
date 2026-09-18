import json

line_pt1 = [718, 286]
line_pt2 = [1608, 984]

def side_of_line(pt):
    vec = [pt[0] - line_pt1[0], pt[1] - line_pt1[1]]
    line_vec = [line_pt2[0] - line_pt1[0], line_pt2[1] - line_pt1[1]]
    normal = [-line_vec[1], line_vec[0]]
    return vec[0] * normal[0] + vec[1] * normal[1]

with open('/home/users/oauser/mvsa/results/vehicle_count_v1/tracks.jsonl', 'r') as f:
    tracks = [json.loads(line) for line in f]

uncounted = [t for t in tracks if not t["crossed"]]

import math
def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

for t1 in uncounted:
    lbox1 = t1.get("last_bbox", t1["creation_bbox"])
    l_bc1 = ((lbox1[0] + lbox1[2]) / 2.0, lbox1[3])
    side1 = side_of_line(l_bc1)
    
    for t2 in uncounted:
        if t1["track_id"] >= t2["track_id"] or t1["class"] != t2["class"]:
            continue
            
        gap = t2["first_frame"] - t1["last_frame"]
        if 0 < gap < 60:
            cbox2 = t2["creation_bbox"]
            c_bc2 = ((cbox2[0] + cbox2[2]) / 2.0, cbox2[3])
            side2 = side_of_line(c_bc2)
            
            if side1 * side2 < 0:
                d = dist(l_bc1, c_bc2)
                if d < 300: # spatially close
                    print(f"FRAGMENTED CROSSING: {t1['class']}")
                    print(f"  Track {t1['track_id']} ends frame {t1['last_frame']} at {l_bc1} (side {side1:.0f})")
                    print(f"  Track {t2['track_id']} starts frame {t2['first_frame']} at {c_bc2} (side {side2:.0f})")
                    print(f"  Gap: {gap} frames, Dist: {d:.1f} pixels")
