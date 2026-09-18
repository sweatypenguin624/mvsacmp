import sys

file_path = '/home/users/oauser/mvsa/scripts/vehicle_counting/Vclassification/main.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
in_loop = False
loop_done = False

for line in lines:
    if "with VideoStreamReader(video_path)" in line and not in_loop and not loop_done:
        in_loop = True
        
        new_loop = """
    time_read = 0.0
    time_inference = 0.0
    time_logic = 0.0
    time_annot = 0.0

    with VideoStreamReader(video_path) as reader:
        read_start = time.time()
        for frame_idx, frame in reader.frames(start_frame=0):
            time_read += time.time() - read_start
            total_frames += 1
            
            inf_start = time.time()
            tracked_results = detector.model.track(
                source=frame,
                persist=True,
                tracker=config["model"]["tracker"],
                verbose=False,
                imgsz=config["model"]["imgsz"],
                device=config["model"]["device"],
                conf=config["model"]["confidence"]
            )
            time_inference += time.time() - inf_start
            
            logic_start = time.time()
            result = tracked_results[0]
            filtered_boxes, f_stats = filt.filter_boxes(result.boxes)
            
            stats_summary["raw_detections"] += f_stats["raw"]
            stats_summary["low_conf"] += f_stats["low_conf"]
            stats_summary["too_small"] += f_stats["too_small"]
            stats_summary["invalid_class"] += f_stats["invalid_class"]
            stats_summary["passed_filter"] += f_stats["passed"]
            
            if filtered_boxes is not None and len(filtered_boxes) > 0:
                active_tracks = tracker.update(frame_idx, filtered_boxes)
            else:
                active_tracks = []
                
            stats_summary["tracks_created"] = len(tracker.tracks)
                
            newly_counted = counter.process_tracks(active_tracks, detector.class_names)
            for nc in newly_counted:
                nc["frame"] = frame_idx
                records.append(nc)
            time_logic += time.time() - logic_start
                
            annot_start = time.time()
            if annotator:
                annotator.draw_line(frame, config["roi"]["counting_line"][0], config["roi"]["counting_line"][1])
                for tid, state, box in active_tracks:
                    stable_class = state.get_stable_class(detector.class_names)
                    conf = state.conf_history[-1] if state.conf_history else 0.0
                    annotator.draw_track(frame, box, tid, stable_class, conf, state.counted)
                annotator.write_frame(frame)
            time_annot += time.time() - annot_start
                
            if total_frames % 100 == 0:
                logger.info(f"Processed {total_frames} frames... Count: {len(counter.counted_ids)}")
                
            if total_frames >= 200:
                logger.info("Stopping at 200 frames for performance testing.")
                break
                
            read_start = time.time()

    if annotator:
        annotator.close()
"""
        new_lines.append(new_loop)
        continue
        
    if in_loop:
        if "elapsed = time.time() - start_time" in line:
            in_loop = False
            loop_done = True
            new_lines.append(line)
        continue
        
    if loop_done and '"processing_fps":' in line:
        new_lines.append(line)
        profiling_str = '        "profiling_sec": {"video_read": time_read, "yolo_inference": time_inference, "filtering_and_logic": time_logic, "annotation": time_annot},\n'
        new_lines.append(profiling_str)
        continue
        
    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

