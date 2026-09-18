import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("tmux ls")
print("Tmux sessions:")
print(stdout.read().decode())
