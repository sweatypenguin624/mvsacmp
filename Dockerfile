FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_DIR=/app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip ffmpeg libsm6 libxext6 tmux wget unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $WORKSPACE_DIR

# 1. Install PyTorch first (pinned)
RUN pip3 install torch==2.1.0+cu118 torchvision==0.16.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# 2. Install Ultralytics and DALI
RUN pip3 install ultralytics==8.4.118 nvidia-dali-cuda110

# 3. Install strict InsightFace requirements (without deps to protect numpy/torch)
RUN pip3 install onnx>=1.14,<1.17 onnxruntime-gpu>=1.16,<1.19 scikit-image>=0.19,<0.23 \
    easydict>=1.10 Cython>=0.29,<3.1 prettytable>=3.6 tqdm>=4.64 Pillow>=9.0 PyYAML>=6.0
RUN pip3 install --no-deps insightface==0.7.3

# 4. Install remaining base requirements
COPY env-working-requirements.txt .
RUN pip3 install -r env-working-requirements.txt

# Download rclone
RUN wget https://downloads.rclone.org/v1.75.0/rclone-v1.75.0-linux-amd64.zip && \
    unzip rclone-v1.75.0-linux-amd64.zip && \
    mkdir -p tools && mv rclone-v1.75.0-linux-amd64 tools/ && \
    rm rclone-v1.75.0-linux-amd64.zip

# Copy application code
COPY . .

# Set entrypoint
RUN chmod +x scripts/deployment/entrypoint.sh
ENTRYPOINT ["scripts/deployment/entrypoint.sh"]
