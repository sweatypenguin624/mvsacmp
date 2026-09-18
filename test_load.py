from ultralytics import YOLO
import sys

print("Loading model...")
try:
    model = YOLO('models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X_a100.engine', task='detect')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load: {e}")
sys.exit(0)
