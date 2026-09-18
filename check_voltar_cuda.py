import paramiko
import time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("voltar", username="oauser", password="welcome123")
stdin, stdout, stderr = ssh.exec_command("export CUDA_VISIBLE_DEVICES=0 && /home/users/oauser/mvsa/env/bin/python -c \"import torch; x = torch.rand(1).cuda(); print('SUCCESS:', x)\" > /home/users/oauser/mvsa/cuda_test.log 2>&1")
status = stdout.channel.recv_exit_status()
