import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("cd /home/users/oauser/mvsa && env/bin/python -c 'import torch; print(\"Name:\", torch.cuda.get_device_name(0))' > torch_out.txt 2>&1")
print("Command sent!")
