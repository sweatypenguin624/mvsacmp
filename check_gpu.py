import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device name: {torch.cuda.get_device_name(0)}")
    print(f"Device count: {torch.cuda.device_count()}")
try:
    x = torch.rand(10, 10).cuda()
    print("Successfully allocated tensor on GPU")
except Exception as e:
    print(f"Error: {e}")
