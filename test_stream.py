import time
from ultralytics import YOLO

m = YOLO('models/UVH-26/weights/YOLOv11-S/UVH-26-MV-YOLOv11-S.pt')

start = time.time()
gen = m.track(source='realrun/test.mp4', persist=True, device='cuda', imgsz=1280, stream=True, verbose=False)
count = 0
for r in gen:
    count += 1
    if count == 500:
        break
print(f"Elapsed for 500 frames: {time.time() - start:.2f}s")
