import numpy as np
from ultralytics import YOLO
from ultralytics.utils import IterableSimpleNamespace
from ultralytics.trackers import BYTETracker
import yaml

model = YOLO("yolo11n.pt")
frame = np.zeros((640, 640, 3), dtype=np.uint8)
res = model.predict(frame)[0]

with open("bytetrack.yaml") as f: # usually in ultralytics/cfg/trackers/bytetrack.yaml
    pass

# We can just let Ultralytics initialize the tracker:
class DummyPredictor:
    def __init__(self):
        self.args = IterableSimpleNamespace(**{"tracker_type": "bytetrack", "track_high_thresh": 0.5, "track_low_thresh": 0.1, "new_track_thresh": 0.6, "track_buffer": 30, "match_thresh": 0.8})
        
tracker = BYTETracker(DummyPredictor().args)
tracks = tracker.update(res, frame)
print("Tracks:", tracks)
