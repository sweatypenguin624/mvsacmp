import os

target = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(target, "r") as f:
    content = f.read()

old_stable = """        needed = min(
            self.min_crossing_frames,
            len(history),
        )

        if needed <= 0:
            return False

        recent = list(history)[-needed:]

        return all(side == previous_side for side in recent)"""

new_stable = """        # Account for the fact that current_side was already appended
        needed = min(
            self.min_crossing_frames,
            len(history) - 1,
        )

        if needed <= 0:
            return False

        recent = list(history)[-(needed + 1):-1]

        return all(side == previous_side for side in recent)"""

if old_stable in content:
    content = content.replace(old_stable, new_stable)
    with open(target, "w") as f:
        f.write(content)
    print("Patched _has_stable_previous_side successfully")
else:
    print("Failed to find old code block")
