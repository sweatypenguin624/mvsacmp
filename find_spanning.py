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

for t in tracks:
    cbox = t["creation_bbox"]
    lbox = t.get("last_bbox", cbox)
    
    c_bc = ((cbox[0] + cbox[2]) / 2.0, cbox[3])
    l_bc = ((lbox[0] + lbox[2]) / 2.0, lbox[3])
    
    c_side = side_of_line(c_bc)
    l_side = side_of_line(l_bc)
    
    if c_side * l_side < 0 and not t["crossed"]:
        print(f"FOUND SPANNING BUT UNCOUNTED: Track {t['track_id']} ({t['class']})")
        print(f"  first frame: {t['first_frame']}, last frame: {t['last_frame']}, lifespan: {t['lifespan']}")
        print(f"  c_bc: {c_bc}, l_bc: {l_bc}")
