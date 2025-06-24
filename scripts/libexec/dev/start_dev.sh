
show_help() {
    echo "Usage: ./start_dev.sh [options]"
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
# Usage: ./scripts/dev/start_dev.sh [options]
# Run with -h or --help for usage information

# =======================================================
# Customer Care AI - Development Environment Starter
# =======================================================
# Starts all required services for local development
# =======================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Default ports
RASA_SERVER_PORT=5005
RASA_ACTIONS_PORT=5055

# Check if Python virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Python virtual environment not activated. Please activate it first.${NC}"
    exit 1
fi

# Function to check if a port is in use
port_in_use() {
    lsof -i ":$1" > /dev/null 2>&1
}

# Function to start Rasa server
start_rasa() {
    # Check if RASA_MODEL_PATH is set
    if [ -z "$RASA_MODEL_PATH" ]; then
        echo -e "${RED}❌ Error: RASA_MODEL_PATH environment variable is required${NC}"
        echo -e "Please set RASA_MODEL_PATH to the path of your Rasa model"
        echo -e "Example: export RASA_MODEL_PATH=/path/to/your/model.tar.gz"
        exit 1
    fi

    # Check if model file exists
    if [ ! -f "$RASA_MODEL_PATH" ]; then
        echo -e "${RED}❌ Error: Model file not found at $RASA_MODEL_PATH${NC}"
        exit 1
    fi

    echo -e "${BLUE}🚀 Starting Rasa server on port ${RASA_SERVER_PORT}...${NC}"
    echo -e "${BLUE}📦 Using model: $RASA_MODEL_PATH${NC}"
    
    rasa run --enable-api --cors "*" --port $RASA_SERVER_PORT --debug \
        --model "$RASA_MODEL_PATH" \
        --endpoints endpoints.yml --credentials credentials.yml &
    RASA_PID=$!
    echo $RASA_PID > /tmp/rasa_server.pid
}

# Function to start Rasa actions server
start_actions() {
    echo -e "${BLUE}🚀 Starting Rasa actions server on port ${RASA_ACTIONS_PORT}...${NC}
    rasa run actions --port $RASA_ACTIONS_PORT --debug &
    ACTIONS_PID=$!
    echo $ACTIONS_PID > /tmp/rasa_actions.pid
}

# Main execution
trap 'echo -e "\n${YELLOW}🛑 Stopping all services...${NC}"; \
    kill $(cat /tmp/rasa_server.pid 2>/dev/null) 2>/dev/null; \
    kill $(cat /tmp/rasa_actions.pid 2>/dev/null) 2>/dev/null; \
    rm -f /tmp/*.pid' EXIT

# Check and start services
if port_in_use $RASA_SERVER_PORT; then
    echo -e "${YELLOW}⚠️  Port ${RASA_SERVER_PORT} is already in use.${NC}"
else
    start_rasa
fi

if port_in_use $RASA_ACTIONS_PORT; then
    echo -e "${YELLOW}⚠️  Port ${RASA_ACTIONS_PORT} is already in use.${NC}"
else
    start_actions
fi

# Show status
echo -e "\n${GREEN}✅ Development environment started successfully!${NC}"
echo -e "${BOLD}Services:${NC}"
echo -e "  • Rasa Server:      http://localhost:${RASA_SERVER_PORT}"
echo -e "  • Rasa Actions:     http://localhost:${RASA_ACTIONS_PORT}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep the script running
wait
