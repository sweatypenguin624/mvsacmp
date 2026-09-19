#!/usr/bin/env bash
# Run this ONCE, immediately after you SSH into the rented GPU box (or, if
# gridshare ever supports pre-provisioned/persistent volumes, run it once
# against that volume BEFORE the billed GPU instance exists -- same script
# either way).
#
# It never touches your laptop. Everything is pulled directly from the old
# server, over SSH, straight onto this box, in parallel, so the GPU-billed
# clock spends as little time as possible on setup instead of inference.
#
# Fill in the two variables below, then run:  bash deploy/bootstrap_gpu_box.sh
set -uo pipefail

# --- EDIT THESE ---
OLD_SERVER="user@old-server-host"                 # SSH target for the box that has the full pipeline
OLD_REPO_ROOT="/path/to/full/pipeline/on/old/server"  # root dir there that contains models/, scripts/, config/, tools/
# -------------------

NEW_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${NEW_REPO_ROOT}/deploy/bootstrap_logs"
mkdir -p "$LOG_DIR"

echo "=== GPU box bootstrap starting: $(date) ==="
echo "Old server: $OLD_SERVER"
echo "Old repo root: $OLD_REPO_ROOT"
echo "New repo root: $NEW_REPO_ROOT"
echo

# Fail fast if we can't even reach the old server -- better to find out now
# than after 10 minutes of a stalled models/ transfer.
if ! ssh -o BatchMode=yes -o ConnectTimeout=10 "$OLD_SERVER" 'echo ok' >/dev/null 2>&1; then
    echo "FATAL: cannot SSH to $OLD_SERVER from this box (no batch/key auth, or no route)."
    echo "Fix SSH access from this box to the old server before re-running."
    exit 1
fi

# rsync --partial keeps whatever bytes made it over if a transfer is
# interrupted, so a re-run resumes instead of re-paying for the whole
# transfer -- important since we're burning rented GPU time while this runs.
RSYNC_OPTS=(-az --partial --info=progress2)

declare -A PIDS

run_job() {
    local name="$1"; shift
    ( "$@" > "${LOG_DIR}/${name}.log" 2>&1 )  &
    PIDS["$name"]=$!
    echo "[launched] $name (pid ${PIDS[$name]}) -- log: ${LOG_DIR}/${name}.log"
}

mkdir -p "${NEW_REPO_ROOT}/models" \
         "${NEW_REPO_ROOT}/scripts" \
         "${NEW_REPO_ROOT}/config" \
         "${NEW_REPO_ROOT}/tools" \
         "${NEW_REPO_ROOT}/vehicle-counting/pipeline/counting"

echo
echo "--- Launching parallel transfers ---"

# Small, fast, unconditionally-required source files -- do these first/fast
# so a code review can start even while models/ is still moving.
run_job "video_utils.py" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/vehicle-counting/pipeline/counting/video_utils.py" \
    "${NEW_REPO_ROOT}/vehicle-counting/pipeline/counting/video_utils.py"

run_job "utils.py" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/vehicle-counting/pipeline/counting/utils.py" \
    "${NEW_REPO_ROOT}/vehicle-counting/pipeline/counting/utils.py"

run_job "scripts_dir" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/scripts/" \
    "${NEW_REPO_ROOT}/scripts/"

run_job "rclone_conf" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/config/rclone.conf" \
    "${NEW_REPO_ROOT}/config/rclone.conf"

run_job "requirements_txt" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/requirements.txt" \
    "${NEW_REPO_ROOT}/requirements.txt"

# Binaries -- moderate size
run_job "rclone_binary" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/tools/rclone-v1.75.0-linux-amd64/" \
    "${NEW_REPO_ROOT}/tools/rclone-v1.75.0-linux-amd64/"

run_job "ffmpeg_bin" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/tools/ffmpeg_bin/" \
    "${NEW_REPO_ROOT}/tools/ffmpeg_bin/"

run_job "ffprobe" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/tools/ffprobe" \
    "${NEW_REPO_ROOT}/tools/ffprobe"

# The big one -- model weights (TensorRT engine + ONNX). This will dominate
# total transfer time; everything above is intentionally launched first so
# it's done well before this finishes.
run_job "models_dir" \
    rsync "${RSYNC_OPTS[@]}" \
    "${OLD_SERVER}:${OLD_REPO_ROOT}/models/" \
    "${NEW_REPO_ROOT}/models/"

echo
echo "--- Waiting for transfers (see ${LOG_DIR}/*.log for live progress) ---"

FAILED=()
for name in "${!PIDS[@]}"; do
    if wait "${PIDS[$name]}"; then
        echo "[done]   $name"
    else
        echo "[FAILED] $name -- see ${LOG_DIR}/${name}.log"
        FAILED+=("$name")
    fi
done

echo
if [ "${#FAILED[@]}" -gt 0 ]; then
    echo "=== ${#FAILED[@]} transfer(s) failed: ${FAILED[*]} ==="
    echo "Re-run this script -- rsync --partial resumes rather than starting over."
    exit 1
fi

chmod +x "${NEW_REPO_ROOT}/tools/rclone-v1.75.0-linux-amd64/rclone" 2>/dev/null
chmod +x "${NEW_REPO_ROOT}/tools/ffmpeg_bin/ffmpeg" 2>/dev/null
chmod +x "${NEW_REPO_ROOT}/tools/ffprobe" 2>/dev/null

echo "=== All transfers complete: $(date) ==="
echo

# Install Python deps while nothing else is running -- this needs network
# but no GPU, so it's cheap relative to the model transfer above.
if [ -f "${NEW_REPO_ROOT}/requirements.txt" ]; then
    echo "--- Installing Python dependencies from requirements.txt ---"
    python3 -m venv "${NEW_REPO_ROOT}/env" 2>/dev/null || true
    source "${NEW_REPO_ROOT}/env/bin/activate"
    pip install -r "${NEW_REPO_ROOT}/requirements.txt"
else
    echo "WARNING: no requirements.txt found on old server at ${OLD_REPO_ROOT}/requirements.txt"
    echo "Generate one there with: pip freeze > requirements.txt  (inside the old server's working venv)"
    echo "then re-run this script, or install dependencies manually before proceeding."
fi

echo
echo "--- Sanity check: verifying everything main.py / orchestrator.py need is present ---"
MISSING=()
check() { [ -e "$1" ] || MISSING+=("$1"); }
check "${NEW_REPO_ROOT}/vehicle-counting/pipeline/counting/video_utils.py"
check "${NEW_REPO_ROOT}/vehicle-counting/pipeline/counting/utils.py"
check "${NEW_REPO_ROOT}/config/rclone.conf"
check "${NEW_REPO_ROOT}/tools/rclone-v1.75.0-linux-amd64/rclone"
check "${NEW_REPO_ROOT}/tools/ffmpeg_bin/ffmpeg"
check "${NEW_REPO_ROOT}/tools/ffprobe"
check "${NEW_REPO_ROOT}/models"

if [ "${#MISSING[@]}" -gt 0 ]; then
    echo "STILL MISSING (fix before running the pipeline for real):"
    for m in "${MISSING[@]}"; do echo "  - $m"; done
    exit 1
fi

echo "All required assets present."
echo "=== Bootstrap complete: $(date) ==="
