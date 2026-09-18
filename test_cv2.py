import cv2
import sys
import time

print("Opening video...")
cap = cv2.VideoCapture("historical-processor/data/videos/cvc10_cam_1/2026-07-23/19.00.00-20.00.00[R][0@0][0].dav.mp4")
if not cap.isOpened():
    print("Failed to open")
    sys.exit(1)
print("Reading frame...")
ret, frame = cap.read()
if ret:
    print(f"Read frame! {frame.shape}")
else:
    print("Failed to read frame")
sys.exit(0)
