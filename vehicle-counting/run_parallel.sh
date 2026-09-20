#!/usr/bin/env bash
# Run several videos through main.py CONCURRENTLY on one GPU.
#
# Why: a single main.py process only uses a fraction of a fast GPU (e.g.
# ~20% on a 5090) because its video decode is CPU-bound and unpipelined --
# the GPU sits idle between frames waiting on the CPU decoder. Running
# several videos at once lets one process's GPU-idle decode gaps get filled
# by another process's inference, without needing NVDEC/DALI at all.
#
# The same video path can be passed more than once (e.g. to load-test
# concurrency without needing extra footage) -- each invocation gets its
# own numbered output dir, so repeats never collide.
#
# Usage:
#   ./run_parallel.sh -c <config.yaml> [-o output_root] [-p max_parallel] [-d duration_minutes] <video1> [video2 ...]
#
#   # Real batch, 5 distinct videos:
#   ./run_parallel.sh -c vehicle-counting/config/vehicle_count_config_cvc3_cam_1.yaml -p 5 test_data/cvc3_cam1/*.mp4
#
#   # Cheap concurrency/utilization test, same file x5, capped to 2 min each:
#   ./run_parallel.sh -c vehicle-counting/config/vehicle_count_config_cvc3_cam_1.yaml -p 5 -d 2 \
#       test_data/cvc3_cam1/sample.mp4 test_data/cvc3_cam1/sample.mp4 test_data/cvc3_cam1/sample.mp4 \
#       test_data/cvc3_cam1/sample.mp4 test_data/cvc3_cam1/sample.mp4
set -uo pipefail

CONFIG=""
OUTPUT_ROOT="results/parallel_run"
MAX_PARALLEL=5
DURATION_MINUTES=""

while getopts "c:o:p:d:" opt; do
  case $opt in
    c) CONFIG="$OPTARG" ;;
    o) OUTPUT_ROOT="$OPTARG" ;;
    p) MAX_PARALLEL="$OPTARG" ;;
    d) DURATION_MINUTES="$OPTARG" ;;
    *) echo "Usage: $0 -c <config.yaml> [-o output_root] [-p max_parallel] [-d duration_minutes] <video1> [video2 ...]"; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

if [ -z "$CONFIG" ] || [ "$#" -eq 0 ]; then
  echo "Usage: $0 -c <config.yaml> [-o output_root] [-p max_parallel] [-d duration_minutes] <video1> [video2 ...]"
  exit 1
fi

if [ ! -f "$CONFIG" ]; then
  echo "FATAL: config not found: $CONFIG"
  exit 1
fi

mkdir -p "$OUTPUT_ROOT"
echo "Running up to $MAX_PARALLEL video(s) at once, output under $OUTPUT_ROOT/"
if [ -n "$DURATION_MINUTES" ]; then
  echo "Capped to $DURATION_MINUTES minute(s) per video (concurrency test mode)"
fi
echo "Watch actual GPU usage in another terminal with: watch -n1 nvidia-smi"
echo

idx=0
for video in "$@"; do
  idx=$((idx + 1))
  base=$(basename "$video")
  base="${base%.*}"
  out_dir="${OUTPUT_ROOT}/${idx}_${base}"
  mkdir -p "$out_dir"

  (
    echo "[START] #${idx} $video -> $out_dir"
    extra_args=()
    if [ -n "$DURATION_MINUTES" ]; then
      extra_args+=(--duration_minutes "$DURATION_MINUTES")
    fi
    python3 vehicle-counting/pipeline/counting/main.py \
      --video "$video" \
      --output_dir "$out_dir" \
      --config "$CONFIG" \
      --no_annotation \
      "${extra_args[@]}" \
      > "$out_dir/stdout.log" 2>&1
    status=$?
    if [ $status -eq 0 ]; then
      echo "[DONE]  #${idx} $video"
    else
      echo "[FAIL]  #${idx} $video (exit $status) -- see $out_dir/stdout.log"
    fi
  ) &

  # Throttle to MAX_PARALLEL concurrent jobs.
  while [ "$(jobs -rp | wc -l)" -ge "$MAX_PARALLEL" ]; do
    wait -n
  done
done

wait
echo
echo "All launched videos finished. Per-video logs are under $OUTPUT_ROOT/<n>_<video_name>/stdout.log"
