#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")/backend"

# Stop any running Rasa processes
echo "🛑 Stopping any running Rasa processes..."
pkill -f "rasa" 2>/dev/null
sleep 2  # Give processes time to terminate

# Find the latest model
LATEST_MODEL=$(ls -t models/*.tar.gz | head -1)
[ -z "$LATEST_MODEL" ] && { echo "❌ No model found in models/ directory"; exit 1; }

# Function to find an available port
find_available_port() {
    local port=$1
    local max_port=5100
    while [ $port -le $max_port ]; do
        if ! (lsof -i :$port >/dev/null 2>&1); then
            echo $port
            return 0
        fi
        echo "Port $port is in use, trying next port..." >&2
        port=$((port + 1))
    done
    echo "❌ Could not find an available port between $1 and $max_port" >&2
    exit 1
}

# Get an available port for the main server
SERVER_PORT=$(find_available_port 5005)

# Get an available port for the action server
ACTION_PORT=5055

# Check if action server port is available
if lsof -i :$ACTION_PORT >/dev/null 2>&1; then
    echo "⚠️  Action server port $ACTION_PORT is in use. Make sure it's the correct action server."
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Please free port $ACTION_PORT or update the script."
        exit 1
    fi
fi

echo "🚀 Starting Rasa shell with model: $(basename "$LATEST_MODEL")"
echo "🌐 Server port: $SERVER_PORT"
echo "🤖 Action server port: $ACTION_PORT"
echo ""
echo "📢 IMPORTANT: Make sure the action server is running in a separate terminal:"
echo "   $ ./start_actions.sh"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Start Rasa shell with the latest model and dynamic port
echo "🔄 Loading model, this may take a moment..."
rasa shell \
  --model "$LATEST_MODEL" \
  --endpoints endpoints.yml \
  --credentials credentials.yml \
  --cors "*" \
  --enable-api \
  --port "$SERVER_PORT"

# If we get here, Rasa shell has exited
echo "\n✅ Rasa shell has been stopped."
echo "   Note: The action server might still be running. Stop it with: pkill -f 'rasa run actions'"
