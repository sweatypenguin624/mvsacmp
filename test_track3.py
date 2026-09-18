import cv2
import numpy as np
import time
from ultralytics import YOLO

m = YOLO('models/UVH-26/weights/YOLOv11-S/UVH-26-MV-YOLOv11-S.pt')
img = np.zeros((1080, 1920, 3), dtype=np.uint8)

start = time.time()
for i in range(10):
    res = m.track(source=img, persist=True, device='cuda', imgsz=1280, verbose=False, classes=[0,1,2], tracker='/home/users/oauser/mvsa/vehicle-counting/config/custom_bytetrack.yaml')
print(f"Elapsed for 10 frames: {time.time() - start:.2f}s")
