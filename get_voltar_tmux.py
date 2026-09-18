import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("tmux capture-pane -pt cam_cvc7_cam_1__eb")
out = stdout.read().decode()
err = stderr.read().decode()
with open("voltar_tmux.log", "w") as f:
    f.write(out + "\n" + err)
