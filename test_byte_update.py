import numpy as np
import torch
from ultralytics.engine.results import Results
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.utils import IterableSimpleNamespace

args = IterableSimpleNamespace(**{"tracker_type": "bytetrack", "track_high_thresh": 0.5, "track_low_thresh": 0.1, "new_track_thresh": 0.6, "track_buffer": 30, "match_thresh": 0.8})
tracker = BYTETracker(args)

# Create mock det
det = torch.tensor([[10, 10, 50, 50, 0.9, 0]]) # x1, y1, x2, y2, conf, cls
img = np.zeros((640, 640, 3), dtype=np.uint8)

try:
    tracks = tracker.update(det, img)
    print("Direct det success:", type(tracks))
except Exception as e:
    print("Direct det failed:", e)

