import os

target = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(target, "r") as f:
    content = f.read()

# Patch __init__
old_init = """        self.frame_count = 0"""
new_init = """        self.frame_count = 0
        self.pending_crossings = {}"""
if old_init in content:
    content = content.replace(old_init, new_init)
else:
    print("Failed to patch __init__")

# Patch _detect_crossing
old_detect = """        # Same side -> no crossing.
        if current_side == previous_side:
            self._update_side_history(tid, current_side)
            return False, None

        # We have a side transition.
        self.stats["crossing_candidates"] += 1

        direction = self.direction_from_sides(
            previous_side,
            current_side,
        )

        # Update state immediately so a noisy oscillation doesn't
        # repeatedly generate the same candidate.
        self.previous_side[tid] = current_side
        self._update_side_history(tid, current_side)

        # Need stable evidence before the transition.
        if not self._has_stable_previous_side(
            tid,
            previous_side,
        ):
            return False, None

        # Need stable evidence after the transition.
        if not self._has_post_crossing_evidence(
            tid,
            current_side,
        ):
            return False, None

        if not self._trajectory_moving_towards_line(
            tid,
            previous_side,
            current_side,
        ):
            return False, None

        # Direction restriction.
        if not self.direction_allowed(direction):
            self.stats["rejected_direction"] += 1
            return False, None

        self.stats["valid_crossings"] += 1

        return True, direction"""

new_detect = """        # Same side -> no crossing.
        if current_side == previous_side:
            self._update_side_history(tid, current_side)
            
            if tid in self.pending_crossings:
                cand_frame, old_side, new_side, cand_dir = self.pending_crossings[tid]
                if current_side == new_side:
                    if self._has_post_crossing_evidence(tid, current_side):
                        del self.pending_crossings[tid]
                        self.stats["valid_crossings"] += 1
                        logger.info(f"CROSSING_CONFIRMED: frame={frame_idx} tid={tid} dir={cand_dir}")
                        return True, cand_dir
                else:
                    del self.pending_crossings[tid]
                    logger.info(f"CROSSING_REJECTED: frame={frame_idx} tid={tid} reverted to previous side before evidence")
                    
            return False, None

        # We have a side transition.
        self.stats["crossing_candidates"] += 1

        direction = self.direction_from_sides(
            previous_side,
            current_side,
        )

        # Update state immediately so a noisy oscillation doesn't
        # repeatedly generate the same candidate.
        self.previous_side[tid] = current_side
        self._update_side_history(tid, current_side)

        # Need stable evidence before the transition.
        if not self._has_stable_previous_side(
            tid,
            previous_side,
        ):
            return False, None

        if not self._trajectory_moving_towards_line(
            tid,
            previous_side,
            current_side,
        ):
            return False, None

        # Direction restriction.
        if not self.direction_allowed(direction):
            self.stats["rejected_direction"] += 1
            return False, None

        self.pending_crossings[tid] = (frame_idx, previous_side, current_side, direction)
        logger.info(f"CROSSING_CANDIDATE: frame={frame_idx} tid={tid} dir={direction}")
        
        if self._has_post_crossing_evidence(tid, current_side):
            del self.pending_crossings[tid]
            self.stats["valid_crossings"] += 1
            logger.info(f"CROSSING_CONFIRMED: frame={frame_idx} tid={tid} dir={direction}")
            return True, direction

        return False, None"""

if old_detect in content:
    content = content.replace(old_detect, new_detect)
else:
    print("Failed to patch _detect_crossing")


# Patch COUNTED log
old_counted = """            self.recent_crossings = [rc for rc in self.recent_crossings if frame_idx - rc[0] < 300]
            
            self.counted_ids.add(tid)
            self.last_crossing_frame[tid] = frame_idx"""
            
new_counted = """            self.recent_crossings = [rc for rc in self.recent_crossings if frame_idx - rc[0] < 300]
            
            self.counted_ids.add(tid)
            self.last_crossing_frame[tid] = frame_idx
            logger.info(f"COUNTED: frame={frame_idx} tid={tid} class={stable_class}")"""

if old_counted in content:
    content = content.replace(old_counted, new_counted)
else:
    print("Failed to patch COUNTED log")

os.remove(target)
with open(target, "w") as f:
    f.write(content)
print("Patched counter.py successfully")
