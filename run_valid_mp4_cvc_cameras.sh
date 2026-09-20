#!/bin/bash
set -e
cd /home/orion/mvsacmp

start_cam() {
    local SESSION_NAME="$1"
    local FOLDER_ID="$2"
    local CAM_NAME="$3"
    local DEVICE="$4"
    local DB_PATH="historical-processor/data/manifest_${CAM_NAME}.db"
    local OUT_DIR="historical-processor/output/${CAM_NAME}"
    local CFG_PATH="vehicle-counting/config/vehicle_count_config_${CAM_NAME}.yaml"

    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux kill-session -t "$SESSION_NAME"
    fi

    echo "Launching $CAM_NAME on GPU $DEVICE"
    tmux new-session -d -s "$SESSION_NAME" \
        "export CUDA_DEVICE_ORDER=PCI_BUS_ID && export CUDA_VISIBLE_DEVICES=$DEVICE && .venv/bin/python historical-processor/orchestrator.py \
            --folder-id '$FOLDER_ID' \
            --camera-name '$CAM_NAME' \
            --db '$DB_PATH' \
            --output-dir '$OUT_DIR' \
            --config '$CFG_PATH' \
            --dl-threads 1 \
            --inf-threads 4 \
            --no-dali \
            --scan"
}

start_cam "cam_cvc3_cam_1" "1eJg_5QzH9FsqK0qxmTfR4PMsiSJUzc6D" "cvc3_cam_1" "0"
start_cam "cam_cvc3_cam_2" "1ZiG88cfCJYDp0NVn9Er9VL3-EeWxpuQc" "cvc3_cam_2" "0"
start_cam "cam_cvc7_cam_2__wb" "1V1JYc8LK4-eKUqeZHony9MlpePR_Ay2e" "cvc7_cam_2__wb" "0"
start_cam "cam_cvc8_cam_1" "1OweqoldHOkOw7L58wqfUQ74MANCJnvN8" "cvc8_cam_1" "0"
start_cam "cam_cvc9_cam_1" "1GZtqT5nLkTn63vTXihsU46BeNoOf2uYm" "cvc9_cam_1" "0"
start_cam "cam_cvc10_cam_1" "1t_RqiwSX4RfT-I0TCQmdgbQATDr2dltw" "cvc10_cam_1" "0"

echo "All VALID MP4 CVC cameras launched!"
