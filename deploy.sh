#!/bin/bash
# One-click deployment script
export CVC_EPHEMERAL_DIR=${CVC_EPHEMERAL_DIR:-/ephemeral/mvsacmp}

# Ensure NVMe ephemeral directory exists
sudo mkdir -p $CVC_EPHEMERAL_DIR
sudo chmod -R 777 $CVC_EPHEMERAL_DIR

# Build image if missing
if [[ "$(docker images -q mvsacmp-pipeline:latest 2> /dev/null)" == "" ]]; then
  ./scripts/deployment/build.sh
fi

# Run container
docker run -d \
  --name mvsacmp-pipeline \
  --gpus all \
  --restart unless-stopped \
  --ipc=host \
  -e RCLONE_CONFIG_TEXT="$RCLONE_CONFIG_TEXT" \
  -v $CVC_EPHEMERAL_DIR:/ephemeral/mvsacmp \
  mvsacmp-pipeline:latest

echo "Pipeline launched. Check logs with: docker logs -f mvsacmp-pipeline"
