import sys
import yaml
sys.path.append("/home/users/oauser/mvsa/vehicle-counting")
from pipeline.Vclassification.counter import VehicleCounter, bottom_center

import numpy as np

# Let's mock a trajectory that crosses the line
line_pt1 = [718, 286]
line_pt2 = [1608, 984]
counter = VehicleCounter(line_pt1, line_pt2, "BOTH")

# 1. Trajectory crossing the finite segment
print("Test 1: Normal crossing")
prev_bc = (1100, 500)
curr_bc = (1100, 800)
crossed, dir_str = counter.check_crossing(prev_bc, curr_bc)
print(f"Normal crossing: {crossed}, {dir_str}")

# 2. Trajectory crossing outside the finite segment
print("\nTest 2: Crossing outside segment")
prev_bc = (500, 200)
curr_bc = (500, 400)
crossed, dir_str = counter.check_crossing(prev_bc, curr_bc)
print(f"Outside segment: {crossed}, {dir_str}")
