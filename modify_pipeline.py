import sys

def modify_batch_runner():
    path = 'scripts/vehicle_counting/batch_runner.py'
    with open(path, 'r') as f:
        content = f.read()
    
    target1 = """    log_msg('Starting batch vehicle counting runner...')
    all_videos = sorted(list(DATASET_DIR.rglob('*.mp4')))
    
    if args.limit is not None:
        all_videos = all_videos[:args.limit]
        log_msg(f'Limiting processing to the first {args.limit} videos.')"""
        
    replacement1 = """    log_msg('Starting batch vehicle counting runner...')
    raw_videos = sorted(list(DATASET_DIR.rglob('*.mp4')))
    
    all_videos = []
    peds_excluded = 0
    for v in raw_videos:
        if "peds - 1 day and 12 hour" in str(v).lower():
            peds_excluded += 1
            continue
        all_videos.append(v)
        
    log_msg(f'Excluded {peds_excluded} videos under the Peds folder.')
    
    if args.limit is not None:
        all_videos = all_videos[:args.limit]
        log_msg(f'Limiting processing to the first {args.limit} videos.')"""
        
    if target1 in content:
        content = content.replace(target1, replacement1)
    else:
        print("Target 1 not found in batch_runner.py")
    
    target2 = """            elif process.returncode == 88:
                status = 'no_detection'
                log_msg(f'[{idx}/{total_videos}] NO DETECTIONS: {video_str} in {elapsed:.2f}s')
                append_list(NO_DETECTION_TXT, video_str)
                counts['no_detection'] += 1"""
                
    replacement2 = """            elif process.returncode == 88:
                status = 'skipped'
                log_msg(f'[{idx}/{total_videos}] SKIPPED: {video_str} in {elapsed:.2f}s')
                append_list(NO_DETECTION_TXT, video_str)
                counts['skipped'] += 1"""
                
    if target2 in content:
        content = content.replace(target2, replacement2)
    else:
        print("Target 2 not found in batch_runner.py")
    
    with open(path, 'w') as f:
        f.write(content)

def modify_main():
    path = 'scripts/vehicle_counting/Vclassification/main.py'
    with open(path, 'r') as f:
        content = f.read()
        
    target = """            if early_detection_check and total_frames <= early_detection_frames:
                if total_frames % 2500 == 0:
                    print(f"EARLY CHECK: {total_frames}/{early_detection_frames} | valid detections: {stats_summary['passed_filter']}")
                    
                if total_frames == early_detection_frames:
                    valid_dets = stats_summary["passed_filter"]
                    if valid_dets >= early_detection_min_detections:
                        print(f"EARLY CHECK PASSED\\nValid detections: {valid_dets}\\n→ CONTINUING FULL PROCESSING")
                    else:
                        print(f"EARLY CHECK COMPLETE\\nValid detections: {valid_dets}\\n→ NO DETECTIONS — SKIPPING VIDEO")
                        if annotator:
                            annotator.close()
                            try:
                                (output_dir / "annotated.mp4").unlink(missing_ok=True)
                            except Exception:
                                pass
                        import sys
                        sys.exit(88)"""
                        
    replacement = """            if early_detection_check and total_frames <= 10000:
                if total_frames % 2500 == 0:
                    print(f"EARLY CHECK: {total_frames}/10000 | valid detections: {stats_summary['passed_filter']}")
                    
                if total_frames == 10000:
                    valid_dets = stats_summary["passed_filter"]
                    if valid_dets >= 1:
                        print(f"EARLY CHECK PASSED\\nValid detections: {valid_dets}\\n→ CONTINUING FULL PROCESSING")
                    else:
                        logger.info("No detections in first 10,000 frames. Skipping video.")
                        print("No detections in first 10,000 frames. Skipping video.")
                        if annotator:
                            annotator.close()
                            try:
                                (output_dir / "annotated.mp4").unlink(missing_ok=True)
                            except Exception:
                                pass
                        import sys
                        sys.exit(88)"""
    
    if target in content:
        content = content.replace(target, replacement)
    else:
        print("Target not found in main.py")
        
    with open(path, 'w') as f:
        f.write(content)

modify_batch_runner()
modify_main()
