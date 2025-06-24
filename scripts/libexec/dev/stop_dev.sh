
show_help() {
    echo "Usage: ./stop_dev.sh [options]"
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
# Usage: ./scripts/dev/stop_dev.sh [options]
# Run with -h or --help for usage information

# =======================================================
# Customer Care AI - Development Environment Stopper
# =======================================================
# Stops all running development services
# =======================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null)
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}🛑 Stopping $service_name (PID: $pid)...${NC}"
            kill -15 "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
            rm -f "$pid_file"
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name process not running${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}⚠️  $service_name not running (PID file not found)${NC}"
    fi
}

# Stop all services
stop_service "Rasa Server" "/tmp/rasa_server.pid"
stop_service "Rasa Actions" "/tmp/rasa_actions.pid"

# Additional cleanup
pkill -f "rasa run" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

echo -e "\n${GREEN}✅ All development services have been stopped${NC}"
