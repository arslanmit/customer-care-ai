
show_help() {
    echo "Usage: ./start_actions.sh [options]"
    echo "  -h, --help   Show this help message and exit"
}

for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            exit 0
            ;;
    esac
done

#!/bin/bash
# Usage: ./scripts/dev/start_actions.sh [options]
# Run with -h or --help for usage information

# Navigate to the script's directory
cd "$(dirname "$0")"

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
