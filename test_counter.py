COUNTER_PATH = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"
with open(COUNTER_PATH, "r") as f:
    counter_code = f.read()

if "recent_crossings" not in counter_code:
    print("recent_crossings not in counter_code")
else:
    print("recent_crossings IS in counter_code")

if "self.counted_ids.add(tid)" in counter_code:
    print("self.counted_ids.add(tid) IS found")
else:
    print("self.counted_ids.add(tid) NOT found")
