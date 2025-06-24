#!/bin/bash

# Default ports
DEFAULT_RASA_PORT=5005
DEFAULT_ACTIONS_PORT=5055

# Function to find and kill process using a port
kill_process_on_port() {
    local port=$1
    local pid
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        pid=$(lsof -ti :$port || true)
    else
        # Linux
        pid=$(lsof -t -i :$port || true)
    fi
    
    if [ -n "$pid" ]; then
        echo "Found process $pid using port $port, killing it..."
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Function to check if a port is available
is_port_available() {
    ! nc -z 127.0.0.1 $1 2>/dev/null
}

# Function to find an available port
find_available_port() {
    local port=$1
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if is_port_available $port; then
            echo $port
            return 0
        fi
        
        kill_process_on_port $port
        
        if is_port_available $port; then
            echo $port
            return 0
        fi
        
        echo "Port $port is in use, trying next port..."
        port=$((port + 1))
        attempt=$((attempt + 1))
    done
    
    echo "ERROR: Could not find an available port after $max_attempts attempts" >&2
    exit 1
}

# Find and clean up ports
echo "=== Setting up Rasa environment ==="

# Kill any existing processes on default ports first
kill_process_on_port $DEFAULT_RASA_PORT
kill_process_on_port $DEFAULT_ACTIONS_PORT

# Find available ports
echo "Finding available ports..."
RASA_PORT=$(find_available_port $DEFAULT_RASA_PORT)
ACTIONS_PORT=$(find_available_port $DEFAULT_ACTIONS_PORT)

echo "✅ Using Rasa port: $RASA_PORT"
echo "✅ Using Actions port: $ACTIONS_PORT"

# Set environment variables
export RASA_MODEL_PATH="$(pwd)/models"
export RASA_ACTIONS_URL="http://localhost:${ACTIONS_PORT}/webhook"

# Function to clean up processes
cleanup() {
    echo -e "\nCleaning up processes..."
    
    # Kill Rasa server if running
    if [ -f ".rasa_server_pid" ]; then
        RASA_PID=$(cat .rasa_server_pid 2>/dev/null)
        if [ -n "$RASA_PID" ] && ps -p $RASA_PID > /dev/null 2>&1; then
            echo "Stopping Rasa server (PID: $RASA_PID)..."
            kill -TERM $RASA_PID 2>/dev/null || true
            sleep 2
            # Force kill if still running
            if ps -p $RASA_PID > /dev/null 2>&1; then
                kill -9 $RASA_PID 2>/dev/null || true
            fi
            rm -f .rasa_server_pid
        fi
    fi
    
    # Kill actions server if running
    if [ -f ".actions_pid" ]; then
        ACTIONS_PID=$(cat .actions_pid 2>/dev/null)
        if [ -n "$ACTIONS_PID" ] && ps -p $ACTIONS_PID > /dev/null 2>&1; then
            echo "Stopping Rasa actions server (PID: $ACTIONS_PID)..."
            kill -TERM $ACTIONS_PID 2>/dev/null || true
            sleep 1
            # Force kill if still running
            if ps -p $ACTIONS_PID > /dev/null 2>&1; then
                kill -9 $ACTIONS_PID 2>/dev/null || true
            fi
            rm -f .actions_pid
        fi
    fi
    
    # Clean up any remaining processes
    pkill -f "rasa run" 2>/dev/null || true
    pkill -f "rasa shell" 2>/dev/null
    
    # Clean up PID files
    rm -f .rasa_server_pid .actions_pid
    
    echo "Cleanup complete."
    exit 0
}

# Set up trap to catch termination signals
trap cleanup INT TERM EXIT

# Navigate to the project root
cd "$(dirname "$0")"

# Set the path to the Rasa project
RASA_DIR="backend/rasa"

# Change to Rasa directory
cd "$RASA_DIR"

# Find the most recent model (macOS compatible)
MODELS_DIR="$(pwd)/models"
MODEL_PATH=$(find "$MODELS_DIR" -name "*.tar.gz" -type f -exec stat -f "%m %N" {} \; | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️  No model found in $MODELS_DIR"
    echo "🚀 Training a new model..."
    rasa train || {
        echo "❌ Failed to train model"
        cleanup
        exit 1
    }
    MODEL_PATH=$(find "$MODELS_DIR" -name "*.tar.gz" -type f -exec stat -f "%m %N" {} \; | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; then
        echo "❌ Failed to find or create model"
        cleanup
        exit 1
    fi
fi

# Create a symlink to the latest model in the models directory
mkdir -p "$MODELS_DIR"
LATEST_MODEL="$MODELS_DIR/latest_model.tar.gz"
ln -sf "$MODEL_PATH" "$LATEST_MODEL"

# Also create a symlink in the current directory for backward compatibility
ln -sf "$MODEL_PATH" "$(pwd)/latest_model.tar.gz"

# Export the full path to the model for Rasa to use
export RASA_MODEL_PATH="$LATEST_MODEL"

echo "✅ Using model: $MODEL_PATH"
echo "✅ Created symlink: $LATEST_MODEL -> $MODEL_PATH"
echo "✅ RASA_MODEL_PATH set to: $RASA_MODEL_PATH"
echo

# Clean up any existing PID files
rm -f .rasa_server_pid .actions_pid

# Start Rasa actions server
echo -e "\n🚀 Starting Rasa actions server on port $ACTIONS_PORT..."
rasa run actions --port $ACTIONS_PORT > actions_server.log 2>&1 &
ACTIONS_PID=$!
echo $ACTIONS_PID > .actions_pid

# Wait for actions server to start
echo "Waiting for actions server to start.."
for i in {1..10}; do
    if curl -s http://localhost:$ACTIONS_PORT >/dev/null; then
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 10 ]; then
        echo -e "\n❌ Failed to start Rasa actions server"
        cat "actions_server.log"
        cleanup
        exit 1
    fi
done

echo -e "\n✅ Actions server is running on port $ACTIONS_PORT\n"

# Start Rasa shell
echo -e "🚀 Starting Rasa shell on port $RASA_PORT..."
rasa shell --port $RASA_PORT --model "$MODEL_PATH" --endpoints "endpoints.yml" --credentials "credentials.yml"
RASA_PID=$!
echo $RASA_PID > .rasa_server_pid

# Wait for the Rasa shell to complete
wait $RASA_PID

# Clean up will be handled by the trap
