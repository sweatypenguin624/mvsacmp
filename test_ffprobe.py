import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("cd /home/users/oauser/mvsa && scripts/tools/ffprobe -i historical-processor/data/videos/cvc10_cam_1/2026-07-23/19.00.00-20.00.00[R][0@0][0].dav.mp4 2>&1")
print(stdout.read().decode())
