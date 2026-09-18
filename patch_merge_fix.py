import re

file_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(file_path, "r") as f:
    content = f.read()

target = """                                logger.info(f"SAFETY NET MERGE: Merging current tid={tid} into lost_tid={lost_tid}, dist={dist:.1f}px")
                                state.counted = True
                                cross_dir = "A_TO_B" if lost_side < 0 else "B_TO_A"
                                if self.direction == "BOTH" or self.direction == cross_dir:
                                    state.crossing_frame = state.last_seen_frame
                                    state.crossing_direction = cross_dir
                                    state.counting_bbox = box.tolist() if hasattr(box, "tolist") else list(box)
                                    state.not_counted_reason = ""
                                    self.counted_ids.add(tid)
                                    self.counts_by_class[stable_class] = self.counts_by_class.get(stable_class, 0) + 1
                                    newly_counted.append({
                                        "track_id": tid,
                                        "class": stable_class,
                                        "direction": cross_dir
                                    })
                                    del self.lost_tracks[lost_tid]
                                    break"""

replacement = """                                logger.info(f"SAFETY NET MERGE: Merging current tid={tid} into lost_tid={lost_tid}, dist={dist:.1f}px")
                                state.counted = True
                                cross_dir = "A_TO_B" if lost_side < 0 else "B_TO_A"
                                if self.direction == "BOTH" or self.direction == cross_dir:
                                    is_duplicate = False
                                    
                                    if not hasattr(self, 'recent_crossings'): self.recent_crossings = []
                                    self.recent_crossings = [(f, d, c, bc, t) for f, d, c, bc, t in self.recent_crossings if self.frame_count - f < 150]
                                    
                                    for rc_frame, rc_dir, rc_class, rc_bc, rc_tid in self.recent_crossings:
                                        if rc_class == stable_class and rc_dir == cross_dir:
                                            import math
                                            rc_dist = math.sqrt((curr_bc[0] - rc_bc[0])**2 + (curr_bc[1] - rc_bc[1])**2)
                                            box_width = box[2] - box[0]
                                            if stable_class == "Bus":
                                                thresh = min(350, max(150, box_width * 0.75))
                                            elif stable_class in ["Truck", "tempo-traveller"]:
                                                thresh = min(300, max(150, box_width * 0.75))
                                            else:
                                                thresh = 150
                                            
                                            if rc_dist < thresh:
                                                logger.info(f"SAFETY NET REJECTION (MERGE PATH): Rejecting tid={tid} as duplicate of class {stable_class}, prev_tid={rc_tid}, dist={rc_dist:.1f}px, thresh={thresh:.1f}px")
                                                is_duplicate = True
                                                break
                                                
                                    if not is_duplicate:
                                        is_frag, frag_reason = self._check_recent_fragment(stable_class, cross_dir, curr_bc, tid)
                                        if is_frag:
                                            logger.info(f"TEMPORAL DEDUP (MERGE PATH): Rejecting tid={tid} as temporal fragment: {frag_reason}")
                                            is_duplicate = True
                                            
                                    state.crossing_frame = state.last_seen_frame
                                    state.crossing_direction = cross_dir
                                    state.counting_bbox = box.tolist() if hasattr(box, "tolist") else list(box)
                                    state.not_counted_reason = "Duplicate" if is_duplicate else ""
                                    
                                    self.counted_ids.add(tid)
                                    if not is_duplicate:
                                        self.counts_by_class[stable_class] = self.counts_by_class.get(stable_class, 0) + 1
                                        self.recent_crossings.append((self.frame_count, cross_dir, stable_class, curr_bc, tid))
                                        newly_counted.append({
                                            "track_id": tid,
                                            "class": stable_class,
                                            "direction": cross_dir
                                        })
                                    else:
                                        self.duplicate_preventions += 1
                                        
                                    del self.lost_tracks[lost_tid]
                                    break"""

if target not in content:
    print("Target not found! Re-checking content:")
    print("Content fragment around line 128:")
    lines = content.split('\n')
    for i, line in enumerate(lines[120:150]):
        print(f"{i+121}: {line}")
else:
    content = content.replace(target, replacement)
    with open(file_path, "w") as f:
        f.write(content)
    print("Successfully patched merge fix.")
