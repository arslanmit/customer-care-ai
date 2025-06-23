#!/bin/bash
cd "$(dirname "$0")"
BUCKET_NAME="$1"
LOG_DIR="logs"

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: No bucket name provided"
    echo "Usage: ./sync_logs_to_gcs.sh BUCKET_NAME"
    exit 1
fi

echo "Syncing logs to gs://$BUCKET_NAME/logs/"
gsutil -m rsync -r "$LOG_DIR" "gs://$BUCKET_NAME/logs/"
echo "Sync completed at $(date)"
