#!/bin/sh
set -e

# Default to info log level if not set
LOG_LEVEL_FLAG=""
if [ "$LOG_LEVEL" = "debug" ]; then
  LOG_LEVEL_FLAG="--debug"
elif [ "$LOG_LEVEL" = "verbose" ]; then
  LOG_LEVEL_FLAG="-v"
fi

# Start Rasa with the configured port and API
# Increase timeout for Cloud Run's health checks
exec python -m rasa run \
    --enable-api \
    --cors "*" \
    --port ${PORT} \
    --endpoints /app/backend/endpoints.yml \
    --credentials /app/backend/credentials.yml \
    --model /app/backend/models \
    --response-timeout 600 \
    $LOG_LEVEL_FLAG
