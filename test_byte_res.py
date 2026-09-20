import numpy as np
from ultralytics import YOLO
from ultralytics.utils import IterableSimpleNamespace
from ultralytics.trackers.byte_tracker import BYTETracker

args = IterableSimpleNamespace(**{"tracker_type": "bytetrack", "track_high_thresh": 0.5, "track_low_thresh": 0.1, "new_track_thresh": 0.6, "track_buffer": 30, "match_thresh": 0.8})
tracker = BYTETracker(args)

model = YOLO("yolo11n.pt")
frame = np.zeros((640, 640, 3), dtype=np.uint8)
res = model.predict(frame)[0]

try:
    tracks = tracker.update(res, frame)
    print("Direct res success:", type(tracks), tracks.shape)
except Exception as e:
    try:
        tracks = tracker.update(res.boxes, frame)
        print("Direct res.boxes success:", type(tracks), tracks.shape)
    except Exception as e2:
        print("Both failed", e2)
