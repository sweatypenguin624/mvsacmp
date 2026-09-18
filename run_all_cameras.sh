#!/bin/bash
set -e
DIR="/home/users/oauser/mvsa"
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
    tmux new-session -d -s "$SESSION_NAME" \
        "/home/users/oauser/mvsa/env/bin/python historical-processor/orchestrator.py \
            --folder-id '$FOLDER_ID' \
            --camera-name '$CAM_NAME' \
            --db '$DB_PATH' \
            --output-dir '$OUT_DIR' \
            --config '$CFG_PATH' \
            --dl-threads 4 \
            --inf-threads 1 \
            --scan"
    echo "[OK] $CAM_NAME started (tmux: $SESSION_NAME)"
}

start_cam "cam_tvc2_cam1"    "1uo3kO-dOtae2kovrp8hhO-8kvObfssZy"      "tvc2_cam1"
start_cam "cam_tvc3_cam1"    "1DQZXCRdauo8IEcNecenXGbiKUzmgp-67"      "tvc3_cam1"
start_cam "cam_tvc4_eb"      "1iOHBQWn89TXU2OrcPBEa-K9zKQ8tlsiP"      "tvc4_cam1_eb"
start_cam "cam_tvc4_wb"      "1VcDjYGSFV_JA6V3BtjVK2pTLV_drX9m5"      "tvc4_cam2_wb"
start_cam "cam_tvc5_eb"      "1fHpvoRMCz0xFK-pWZm_CyW1tTGAQkWmB"      "tvc5_cam1_eb"
start_cam "cam_tvc5_wb"      "14INUpnOHhrVy1t3_JQkWtrIEpRr3ZgCE"      "tvc5_cam2_wb"
start_cam "cam_tvc6_nb"      "1UhELkjqKlG-OcsAqrnHN9HgYet3e3zFZ"      "tvc6_cam1_nb"
start_cam "cam_tvc6_sb"      "1_GidlTKc-Kvp-8hILi90quMEOOOaSpHF"      "tvc6_cam2_sb"
start_cam "cam_tvc7_nb"      "18Oi-fyV8w5MPqfO4v12WDT6stcohhDho"      "tvc7_cam1_nb"
start_cam "cam_tvc7_sb"      "1Akg2gJd_bBLqfEMZ3kK-0xnf0RfFg1sU"      "tvc7_cam2_sb"
start_cam "cam_tvc8_cam1"    "1iT_LjMtQoyIFam_Akl2eJvs0Q0c80xav"      "tvc8_cam1"

echo ""
echo "All camera orchestrators launched. Use 'tmux ls' to view sessions."
