#!/usr/bin/env bash
# Run several videos through main.py CONCURRENTLY on one GPU.
#
# Why: a single main.py process only uses a fraction of a fast GPU (e.g.
# ~20% on a 5090) because its video decode is CPU-bound and unpipelined --
# the GPU sits idle between frames waiting on the CPU decoder. Running
# several videos at once lets one process's GPU-idle decode gaps get filled
# by another process's inference, without needing NVDEC/DALI at all.
#
# Usage:
#   ./run_parallel.sh -c <config.yaml> [-o output_root] [-p max_parallel] <video1> [video2 ...]
#   ./run_parallel.sh -c vehicle-counting/config/vehicle_count_config_cvc3_cam_1.yaml -p 5 test_data/cvc3_cam1/*.mp4
set -uo pipefail

CONFIG=""
OUTPUT_ROOT="results/parallel_run"
MAX_PARALLEL=5

while getopts "c:o:p:" opt; do
  case $opt in
    c) CONFIG="$OPTARG" ;;
    o) OUTPUT_ROOT="$OPTARG" ;;
    p) MAX_PARALLEL="$OPTARG" ;;
    *) echo "Usage: $0 -c <config.yaml> [-o output_root] [-p max_parallel] <video1> [video2 ...]"; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

if [ -z "$CONFIG" ] || [ "$#" -eq 0 ]; then
  echo "Usage: $0 -c <config.yaml> [-o output_root] [-p max_parallel] <video1> [video2 ...]"
  exit 1
fi

if [ ! -f "$CONFIG" ]; then
  echo "FATAL: config not found: $CONFIG"
  exit 1
fi

mkdir -p "$OUTPUT_ROOT"
echo "Running up to $MAX_PARALLEL video(s) at once, output under $OUTPUT_ROOT/"
echo "Watch actual GPU usage in another terminal with: watch -n1 nvidia-smi"
echo

printf '%s\n' "$@" | xargs -P "$MAX_PARALLEL" -I {} bash -c '
  video="$1"
  cfg="$2"
  out_root="$3"
  base=$(basename "$video")
  base="${base%.*}"
  out_dir="${out_root}/${base}"
  mkdir -p "$out_dir"
  echo "[START] $video -> $out_dir"
  python3 vehicle-counting/pipeline/counting/main.py \
    --video "$video" \
    --output_dir "$out_dir" \
    --config "$cfg" \
    --no_annotation \
    > "$out_dir/stdout.log" 2>&1
  status=$?
  if [ $status -eq 0 ]; then
    echo "[DONE]  $video"
  else
    echo "[FAIL]  $video (exit $status) -- see $out_dir/stdout.log"
  fi
' _ {} "$CONFIG" "$OUTPUT_ROOT"

echo
echo "All launched videos finished. Per-video logs are under $OUTPUT_ROOT/<video_name>/stdout.log"
