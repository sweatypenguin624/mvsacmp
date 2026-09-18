import numpy as np
from ultralytics import YOLO

m = YOLO('models/UVH-26/weights/YOLOv11-S/UVH-26-MV-YOLOv11-S.pt')

# Create a sequence of 3 frames with a moving square
frames = []
for i in range(3):
    img = np.zeros((640, 640, 3), dtype=np.uint8)
    # Draw a mock car (a white box) moving right
    x = 100 + i * 20
    img[200:300, x:x+100] = 255
    frames.append(img)

# Try batch tracking
results = m.track(source=frames, persist=True, device='cuda', imgsz=640, verbose=False, classes=[0,1,2,3,4,5,6,7,8]) # use some common classes
for i, r in enumerate(results):
    print(f"Frame {i}: tracks {r.boxes.id}")
