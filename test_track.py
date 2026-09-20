import numpy as np
from ultralytics import YOLO

model = YOLO("yolo11n.pt") # fallback small model
frames = [np.zeros((640, 640, 3), dtype=np.uint8) for _ in range(3)]
results = model.track(frames, persist=True)
print("Results:", type(results), len(results))
