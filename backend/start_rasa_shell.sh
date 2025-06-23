#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")"

# Stop any running Rasa shell processes (but not action server)
echo "🛑 Stopping any running Rasa shell processes..."
pkill -f "rasa shell" 2>/dev/null
sleep 2

# Find the latest model
echo "🔍 Finding latest model..."
LATEST_MODEL=$(find models -type f -name "*.tar.gz" -exec ls -t {} + | head -n 1)

if [ -z "$LATEST_MODEL" ]; then
    echo "❌ No model found in the models/ directory. Please train a model first."
    exit 1
fi

# Function to check if a port is in use
port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is not in use
    fi
}

# Find an available port for the Rasa server
find_available_port() {
    local port=5005
    while port_in_use $port; do
        echo "Port $port is in use, trying next port..." >&2
        port=$((port + 1))
    done
    echo $port
}

# Check if action server is running on the default port (5055)
ACTION_PORT=5055
if port_in_use $ACTION_PORT; then
    echo "✅ Action server is already running on port $ACTION_PORT"
    ACTION_SERVER_STARTED_BY_ME=false
else
    echo "⚠️  Action server is not running. Starting it now..."
    ./start_actions.sh > action_server.log 2>&1 &
    ACTION_SERVER_PID=$!
    ACTION_SERVER_STARTED_BY_ME=true
    
    # Give it a moment to start
    sleep 5
    
    # Verify it started successfully
    if ! port_in_use $ACTION_PORT; then
        echo "❌ Failed to start action server. Check action_server.log for details."
        exit 1
    fi
    echo "✅ Action server started successfully on port $ACTION_PORT"
fi

# Get an available port for the Rasa server
SERVER_PORT=$(find_available_port)

# If the selected port is the action server port, find another one
if [ "$SERVER_PORT" -eq "$ACTION_PORT" ]; then
    SERVER_PORT=$((SERVER_PORT + 1))
    
    # If the new port is in use, find the next available
    while port_in_use $SERVER_PORT; do
        SERVER_PORT=$((SERVER_PORT + 1))
    done
fi

echo "🚀 Starting Rasa shell with model: $(basename "$LATEST_MODEL")"
echo "🌐 Server port: $SERVER_PORT"
echo "🤖 Action server port: $ACTION_PORT"

# Function to clean up when this script exits
cleanup() {
    echo "\n🔄 Cleaning up..."
    
    # Only kill the action server if we started it
    if [ "$ACTION_SERVER_STARTED_BY_ME" = true ]; then
        echo "🛑 Stopping action server (PID: $ACTION_SERVER_PID)..."
        pkill -P $ACTION_SERVER_PID 2>/dev/null
        kill $ACTION_SERVER_PID 2>/dev/null
        rm -f action_server.log
    fi
    
    echo "✅ Cleanup complete."
}

# Set up trap to ensure cleanup runs on script exit
trap cleanup EXIT

# Start Rasa shell with the latest model and dynamic port
echo "🔄 Loading model, this may take a moment..."
rasa shell \
  --model "$LATEST_MODEL" \
  --endpoints endpoints.yml \
  --credentials credentials.yml \
  --cors "*" \
  --enable-api \
  --port "$SERVER_PORT"
