counter_path = "/home/users/oauser/mvsa/vehicle-counting/pipeline/counting/counter.py"

with open(counter_path, 'r') as f:
    counter_code = f.read()

# Replace {t} with {rc_tid} in the log statement
counter_code = counter_code.replace("prev_tid={t}", "prev_tid={rc_tid}")

with open(counter_path, 'w') as f:
    f.write(counter_code)

print("Fixed the variable name.")
