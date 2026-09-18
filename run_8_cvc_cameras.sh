#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

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
        "export CUDA_VISIBLE_DEVICES=$DEVICE && /home/users/oauser/mvsa/env/bin/python historical-processor/orchestrator.py \
            --folder-id '$FOLDER_ID' \
            --camera-name '$CAM_NAME' \
            --db '$DB_PATH' \
            --output-dir '$OUT_DIR' \
            --config '$CFG_PATH' \
            --dl-threads 16 \
            --inf-threads 4 \
            --scan"
}

start_cam "cam_cvc3" "1471o4gcuNTUerIRm7QIj6nvCFwXWhwyk" "cvc3" "0"
start_cam "cam_cvc4" "1u5oo6FfzkXSObybW12teSH9u2nTPWQwC" "cvc4" "0"
start_cam "cam_cvc5" "1ekMGsormVsfO9NO3o9Us5-Q6cx1297HX" "cvc5" "0"
start_cam "cam_cvc6" "1RaF2p92Rirj5CwnVgqH3e2A0VHihr-Iv" "cvc6" "0"

start_cam "cam_cvc7" "1K3k8RXDAvcSD4vuuXbL_jWwXivphORb6" "cvc7" "1"
start_cam "cam_cvc8" "1yOdHYE3EFZimAslSZx99zIhdDZ3WSrJp" "cvc8" "1"

start_cam "cam_cvc9" "1bggk1ddkr5QyXQZS0sHUY-lbv9WuFaG6" "cvc9" "2"
start_cam "cam_cvc10" "1rg5Jpt0Reane34A97YehEfJGvOBr2X8S" "cvc10" "2"

echo "All 8 cameras launched!"
