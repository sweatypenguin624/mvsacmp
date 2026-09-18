#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

start_cam() {
    local SESSION_NAME="$1"
    local FOLDER_ID="$2"
    local CAM_NAME="$3"
    local DB_PATH="historical-processor/data/manifest_${CAM_NAME}.db"
    local OUT_DIR="historical-processor/output/${CAM_NAME}"
    local CFG_PATH="vehicle-counting/config/vehicle_count_config_${CAM_NAME}.yaml"

    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo "[!] tmux session '$SESSION_NAME' already exists. Restarting cleanly..."
        tmux kill-session -t "$SESSION_NAME"
    fi

    echo "[+] Launching $CAM_NAME in tmux session '$SESSION_NAME'..."
    echo "    Folder ID: $FOLDER_ID"
    echo "    Config:    $CFG_PATH"
    echo "    DB:        $DB_PATH"
    echo "    Output:    $OUT_DIR"

    tmux new-session -d -s "$SESSION_NAME" \
        "/home/users/oauser/mvsa/env/bin/python historical-processor/orchestrator.py \
            --folder-id '$FOLDER_ID' \
            --camera-name '$CAM_NAME' \
            --db '$DB_PATH' \
            --output-dir '$OUT_DIR' \
            --config '$CFG_PATH' \
            --dl-threads 4 \
            --inf-threads 2 \
            --scan"
    echo "[✓] $CAM_NAME started successfully in background (tmux session: $SESSION_NAME)"
    echo "--------------------------------------------------------------------------------"
}

echo "================================================================================"
echo " Starting Historical Processor Pipeline for 6 Camera Folders"
echo "================================================================================"

# 1. TVC 1 - Cam 1 (Northbound)
start_cam "cam_tvc1_nb"  "1uo3kO-dOtae2kovrp8hhO-8kvObfssZy" "tvc1_cam1_nb"

# 2. TVC 1 - Cam 2 (Southbound)
start_cam "cam_tvc1_sb"  "1DQZXCRdauo8IEcNecenXGbiKUzmgp-67" "tvc1_cam2_sb"

# 3. CVC 11 - Cam 3 (Eastbound)
start_cam "cam_cvc11_eb" "1iOHBQWn89TXU2OrcPBEa-K9zKQ8tlsiP" "cvc11_cam3_eb"

# 4. CVC 11 - Cam 4 (Westbound)
start_cam "cam_cvc11_wb" "1VcDjYGSFV_JA6V3BtjVK2pTLV_drX9m5" "cvc11_cam4_wb"

# 5. CVC 6 - Cam 3 (Northbound)
start_cam "cam_cvc6_nb"  "1UhELkjqKlG-OcsAqrnHN9HgYet3e3zFZ" "cvc6_cam3_nb"

# 6. CVC 6 - Cam 4 (Southbound)
start_cam "cam_cvc6_sb"  "1_GidlTKc-Kvp-8hILi90quMEOOOaSpHF" "cvc6_cam4_sb"

echo ""
echo "All 6 camera orchestrators are running in parallel tmux sessions!"
echo "Use 'tmux ls' to view active sessions."
echo "Use 'tmux attach -t <session_name>' to view a specific camera pipeline."
