import sys
import yaml
from pathlib import Path
import cv2

sys.path.append("/home/users/oauser/mvsa/vehicle-counting")
from pipeline.Vclassification.detector import VehicleDetector
from pipeline.Vclassification.filters import DetectionFilter
from pipeline.Vclassification.tracker import VehicleTracker
from pipeline.Vclassification.counter import VehicleCounter, bottom_center

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

config_path = "/home/users/oauser/mvsa/vehicle-counting/config/vehicle_count_config.yaml"
config = load_config(config_path)

detector = VehicleDetector(
    model_path="/storage/users/oauser/mvsa/models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X.pt",
    device=config["model"]["device"],
    conf_thres=config["model"]["confidence"],
    imgsz=config["model"]["imgsz"]
)

filt = DetectionFilter(
    min_area=config["filters"]["min_box_area"],
    min_width=config["filters"]["min_width"],
    min_height=config["filters"]["min_height"],
    class_names=detector.class_names
)

tracker = VehicleTracker(min_track_frames=config["tracker"]["min_track_frames"])

line_pt1 = config["roi"]["counting_line"][0]
line_pt2 = config["roi"]["counting_line"][1]
counter = VehicleCounter(line_pt1, line_pt2, config["roi"]["count_direction"])

cap = cv2.VideoCapture("/home/users/oauser/mvsa/videos/sample.mp4")

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    tracked_results = detector.model.track(
        source=frame,
        persist=True,
        tracker="/home/users/oauser/mvsa/vehicle-counting/config/custom_bytetrack.yaml", # default
        verbose=False,
        imgsz=config["model"]["imgsz"],
        device=config["model"]["device"],
        conf=config["model"]["confidence"]
    )
    results = tracked_results[0]
    filtered_boxes, _ = filt.filter_boxes(results.boxes)
    class_names = detector.class_names
    
    active_tracks = tracker.update(frame_idx, filtered_boxes)
    
    if 450 <= frame_idx <= 491:
        print(f"\n--- FRAME {frame_idx} --- RAW DETECTIONS ---")
        if filtered_boxes is not None and len(filtered_boxes) > 0:
            boxes = filtered_boxes.xyxy.cpu().numpy()
            confidences = filtered_boxes.conf.cpu().numpy()
            class_ids = filtered_boxes.cls.cpu().numpy().astype(int)
            for b, c, cid in zip(boxes, confidences, class_ids):
                if b[0] > 600 and b[1] > 0:
                    print(f"Raw YOLO: bbox={b.tolist()}, conf={c:.2f}, class={class_names[cid]}")
        
        print(f"--- FRAME {frame_idx} --- TRACKS ---")
        for tid, state, bbox in active_tracks:
            bc = bottom_center(bbox)
            side = counter.side_of_line(bc)
            print(f"TRACK {tid}: bbox={bbox.tolist()}, bc={bc}, side={side:.2f}, class={state.get_stable_class(class_names)}")
            
    if frame_idx > 491:
        break
        
    frame_idx += 1

cap.release()
