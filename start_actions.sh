#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")/backend"

# Stop any running action servers
echo "🛑 Stopping any running Rasa action servers..."
pkill -f "rasa run actions" 2>/dev/null
sleep 2

# Set environment variables to reduce noise
export RASA_SDK_ENABLE_METRICS="false"
export PYTHONUNBUFFERED=1

echo "🚀 Starting Rasa Action Server..."
rasa run actions \
  --actions actions \
  --port 5055 \
  --debug

echo "\n✅ Rasa Action Server has been stopped."
