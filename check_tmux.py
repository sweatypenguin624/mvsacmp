import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("/usr/bin/tmux capture-pane -p -t cam_cvc10_cam_1")
print("STDOUT:")
print(stdout.read().decode())
print("STDERR:")
print(stderr.read().decode())
