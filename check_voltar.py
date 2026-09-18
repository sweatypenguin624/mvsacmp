import paramiko
import time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("cd /home/users/oauser/mvsa && export CUDA_DEVICE_ORDER=PCI_BUS_ID && export CUDA_VISIBLE_DEVICES=0 && env/bin/python vehicle-counting/pipeline/counting/main.py --video historical-processor/data/videos/cvc7_cam_1__eb/2026-07-22/15.00.00-16.00.00[R][0@0][0].dav.mp4 --output_dir historical-processor/output/cvc7_cam_1__eb/2026-07-22/15.00.00-16.00.00 --no_annotation --start_time 15:00:00 --config vehicle-counting/config/vehicle_count_config_cvc7_cam_1__eb.yaml > crash_test.log 2>&1")
time.sleep(10)
stdin, stdout, stderr = ssh.exec_command("cat /home/users/oauser/mvsa/crash_test.log")
time.sleep(2)
print("CRASH LOG:\n", stdout.read().decode())
