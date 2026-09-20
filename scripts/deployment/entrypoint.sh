#!/bin/bash
set -e

echo "=== Starting Pipeline Initialization ==="

# 1. Inject Rclone Config
mkdir -p ~/.config/rclone
if [ -n "$RCLONE_CONFIG_TEXT" ]; then
    echo "$RCLONE_CONFIG_TEXT" > ~/.config/rclone/rclone.conf
    echo "Rclone config injected."
else
    echo "WARNING: RCLONE_CONFIG_TEXT environment variable is not set."
fi

# 2. TensorRT JIT Compilation (Cache Strategy)
export ENGINE_CACHE_DIR="/ephemeral/mvsacmp/engine_cache"
mkdir -p $ENGINE_CACHE_DIR

# Determine GPU Architecture (e.g. 80 for A100, 90 for H100)
GPU_ARCH=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -n 1 | tr -d '.')
YOLO_MODEL_PT="models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X.pt"
TARGET_ENGINE="$ENGINE_CACHE_DIR/UVH-26-MV-YOLOv11-X_sm${GPU_ARCH}.engine"

if [ ! -f "$TARGET_ENGINE" ]; then
    echo "TensorRT engine for Compute Capability $GPU_ARCH not found. Building..."
    # A modified export_trt.py that takes target dest as argument
    python3 historical-processor/export_trt_dynamic.py --source $YOLO_MODEL_PT --dest $TARGET_ENGINE
else
    echo "Found cached TensorRT engine for Compute Capability $GPU_ARCH: $TARGET_ENGINE"
fi

# Link the built engine to the expected path so existing YAML configs work without changes
ln -sf "$TARGET_ENGINE" "models/UVH-26/weights/YOLOv11-X/UVH-26-MV-YOLOv11-X.engine"

# 3. Launch Orchestrator (Example: run_11_cvc_cameras.sh or directly)
echo "=== Launching Orchestrator ==="
exec ./run_11_cvc_cameras_docker.sh
