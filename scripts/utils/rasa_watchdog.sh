
show_help() {
    echo "Usage: ./rasa_watchdog.sh [options]"
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
# Usage: ./scripts/utils/rasa_watchdog.sh [options]
# Run with -h or --help for usage information

# =========================================================
# RASA Watchdog Script
# =========================================================
# This script:
# 1. Monitors RASA server processes
# 2. Automatically restarts if they crash
# 3. Logs restart attempts and status
# =========================================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CHECK_INTERVAL=30  # seconds between checks
MAX_RESTART_ATTEMPTS=5  # maximum number of consecutive restart attempts
RESTART_COOLDOWN=300  # seconds to wait after reaching max attempts
LOG_DIR="logs"
WATCHDOG_LOG="$LOG_DIR/rasa_watchdog.log"

# Navigate to the script's directory
cd "$(dirname "$0")"

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR

log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$message" >> "$WATCHDOG_LOG"
    echo -e "$message"
}

restart_rasa() {
    log "${YELLOW}⚠️ RASA server down, attempting restart...${NC}"
    
    # Kill any hanging processes
    pkill -f "rasa run" || true
    sleep 2
    
    # Start RASA in API mode
    ./start_rasa_shell.sh --run-mode api >> "$LOG_DIR/rasa_restart.log" 2>&1 &
    
    # Wait for startup
    sleep 10
    
    # Check if it started successfully
    if pgrep -f "rasa run" > /dev/null; then
        log "${GREEN}✅ RASA server restarted successfully${NC}"
        return 0
    else
        log "${RED}❌ Failed to restart RASA server${NC}"
        return 1
    fi
}

restart_action_server() {
    log "${YELLOW}⚠️ Action server down, attempting restart...${NC}"
    
    # Kill any hanging processes
    pkill -f "rasa run actions" || true
    sleep 2
    
    # Start action server
    ./start_actions.sh >> "$LOG_DIR/action_restart.log" 2>&1 &
    
    # Wait for startup
    sleep 5
    
    # Check if it started successfully
    if pgrep -f "rasa run actions" > /dev/null; then
        log "${GREEN}✅ Action server restarted successfully${NC}"
        return 0
    else
        log "${RED}❌ Failed to restart action server${NC}"
        return 1
    fi
}

log "${BLUE}🔄 Starting RASA watchdog service...${NC}"

# Main monitoring loop
consecutive_failures=0
while true; do
    rasa_running=false
    action_running=false
    
    # Check if RASA is running
    if pgrep -f "rasa run" > /dev/null; then
        rasa_running=true
    fi
    
    # Check if action server is running
    if pgrep -f "rasa run actions" > /dev/null; then
        action_running=true
    fi
    
    # Handle RASA server status
    if [ "$rasa_running" = false ]; then
        if [ $consecutive_failures -lt $MAX_RESTART_ATTEMPTS ]; then
            restart_rasa
            if [ $? -eq 0 ]; then
                consecutive_failures=0
            else
                consecutive_failures=$((consecutive_failures + 1))
            fi
        else
            log "${RED}❌ Reached maximum restart attempts ($MAX_RESTART_ATTEMPTS)${NC}"
            log "${YELLOW}⚠️ Cooling down for $RESTART_COOLDOWN seconds...${NC}"
            sleep $RESTART_COOLDOWN
            consecutive_failures=0
        fi
    fi
    
    # Handle action server status
    if [ "$action_running" = false ]; then
        restart_action_server
    fi
    
    # If both are running, reset failure counter
    if [ "$rasa_running" = true ] && [ "$action_running" = true ]; then
        if [ $consecutive_failures -gt 0 ]; then
            log "${GREEN}✅ All services running normally again${NC}"
            consecutive_failures=0
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
