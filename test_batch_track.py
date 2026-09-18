import cv2
import numpy as np
import time
from ultralytics import YOLO

m = YOLO('models/UVH-26/weights/YOLOv11-S/UVH-26-MV-YOLOv11-S.pt')
batch = [np.zeros((1080, 1920, 3), dtype=np.uint8) for _ in range(16)]

start = time.time()
res = m.track(source=batch, persist=True, device='cuda', imgsz=1280, verbose=False)
print(f"Elapsed for batch of 16: {time.time() - start:.2f}s")
