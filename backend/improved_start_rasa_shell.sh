#!/bin/bash

# =========================================================
# Enhanced RASA Shell Script
# =========================================================
# Features:
# - Command line arguments for custom configuration
# - Colorized output for better readability
# - Robust error handling and validation
# - Dynamic port selection with proper verification
# - Health checks for dependencies and services
# - Support for different RASA modes (shell, api, debug)
# - Improved cleanup handling for graceful termination
# =========================================================

# ANSI color codes for better output readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Default configuration values
DEFAULT_ACTION_PORT=5055
DEFAULT_SERVER_PORT=5005
MAX_RETRY_ATTEMPTS=30
RETRY_INTERVAL=1
DEFAULT_MODE="shell"
LOG_FILE="rasa_shell.log"
DEBUG=false
DEFAULT_ENDPOINTS="endpoints.yml"
DEFAULT_CREDENTIALS="credentials.yml"

# Parse command line arguments
usage() {
    echo -e "${BOLD}Usage:${NC} $0 [options]"
    echo -e "${BOLD}Options:${NC}"
    echo -e "  ${CYAN}-m, --model MODEL${NC}        Specific model file to use (defaults to latest)"
    echo -e "  ${CYAN}-p, --port PORT${NC}          Custom server port (default: $DEFAULT_SERVER_PORT)"
    echo -e "  ${CYAN}-a, --action-port PORT${NC}   Custom action server port (default: $DEFAULT_ACTION_PORT)"
    echo -e "  ${CYAN}-e, --endpoints FILE${NC}     Custom endpoints file (default: $DEFAULT_ENDPOINTS)"
    echo -e "  ${CYAN}-c, --credentials FILE${NC}   Custom credentials file (default: $DEFAULT_CREDENTIALS)"
    echo -e "  ${CYAN}-x, --no-action${NC}          Skip action server startup checks"
    echo -e "  ${CYAN}-d, --debug${NC}              Enable debug mode"
    echo -e "  ${CYAN}-r, --run-mode MODE${NC}      Run mode [shell, api, debug] (default: shell)"
    echo -e "  ${CYAN}-h, --help${NC}               Show this help message"
    exit 1
}

# Process command line arguments
MODEL_PATH=""
SERVER_PORT=$DEFAULT_SERVER_PORT
ACTION_PORT=$DEFAULT_ACTION_PORT
ENDPOINTS_FILE=$DEFAULT_ENDPOINTS
CREDENTIALS_FILE=$DEFAULT_CREDENTIALS
SKIP_ACTION=false
RUN_MODE=$DEFAULT_MODE

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -m|--model) MODEL_PATH="$2"; shift ;;
        -p|--port) SERVER_PORT="$2"; shift ;;
        -a|--action-port) ACTION_PORT="$2"; shift ;;
        -e|--endpoints) ENDPOINTS_FILE="$2"; shift ;;
        -c|--credentials) CREDENTIALS_FILE="$2"; shift ;;
        -x|--no-action) SKIP_ACTION=true ;;
        -d|--debug) DEBUG=true ;;
        -r|--run-mode) RUN_MODE="$2"; shift ;;
        -h|--help) usage ;;
        *) echo -e "${RED}Error: Unknown parameter: $1${NC}" >&2; usage ;;
    esac
    shift
done

# Validate run mode
if [[ ! "$RUN_MODE" =~ ^(shell|api|debug)$ ]]; then
    echo -e "${RED}Error: Invalid run mode '$RUN_MODE'. Must be 'shell', 'api', or 'debug'.${NC}" >&2
    exit 1
fi

# Function to log messages with timestamps
log() {
    local level=$1
    local message=$2
    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}ℹ️  ${ts} - ${message}${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅ ${ts} - ${message}${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  ${ts} - ${message}${NC}" >&2
            ;;
        "ERROR")
            echo -e "${RED}❌ ${ts} - ${message}${NC}" >&2
            ;;
        *)
            echo -e "${ts} - ${message}"
            ;;
    esac
    
    # Log to file if debug is enabled
    if [ "$DEBUG" = true ]; then
        echo "${ts} - [${level}] ${message}" >> "$LOG_FILE"
    fi
}

# Navigate to the backend directory
cd "$(dirname "$0")"

log "INFO" "Starting Rasa shell script in $RUN_MODE mode"

# Check for required dependencies
check_dependencies() {
    log "INFO" "Checking dependencies..."
    
    for cmd in rasa lsof find pkill; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            log "ERROR" "Required command not found: $cmd"
            exit 1
        fi
    done
    
    log "SUCCESS" "All required dependencies are available"
}
check_dependencies

# Function to check if a port is in use
port_in_use() {
    local port=$1
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is not in use
    fi
}

# Find an available port for the Rasa server
find_available_port() {
    local start_port=$1
    local port=$start_port
    local attempts=0
    local max_attempts=50
    
    while [ $attempts -lt $max_attempts ]; do
        if ! port_in_use "$port"; then
            echo "$port"
            return 0
        fi
        log "WARNING" "Port $port is in use, trying next port..."
        port=$((port + 1))
        attempts=$((attempts + 1))
    done
    
    log "ERROR" "Could not find an available port after $max_attempts attempts"
    exit 1
}

# Stop any running Rasa shell processes
log "INFO" "Stopping any running Rasa shell processes..."
pkill -f "rasa shell" 2>/dev/null || true
sleep 2

# Find the latest model if not specified
if [ -z "$MODEL_PATH" ]; then
    log "INFO" "Finding latest model..."
    if [ -d "models" ]; then
        MODEL_PATH=$(find models -type f -name "*.tar.gz" -exec ls -t {} + 2>/dev/null | head -n 1)
    fi
    
    if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; then
        log "ERROR" "No model found in the models/ directory. Please train a model first."
        exit 1
    fi
    
    log "SUCCESS" "Using model: $(basename "$MODEL_PATH")"
else
    if [ ! -f "$MODEL_PATH" ]; then
        log "ERROR" "Specified model file does not exist: $MODEL_PATH"
        exit 1
    fi
fi

# Ensure endpoints and credentials files exist
if [ ! -f "$ENDPOINTS_FILE" ]; then
    log "WARNING" "Endpoints file '$ENDPOINTS_FILE' not found, using default endpoints.yml"
    ENDPOINTS_FILE="endpoints.yml"
fi

if [ ! -f "$CREDENTIALS_FILE" ]; then
    log "WARNING" "Credentials file '$CREDENTIALS_FILE' not found, using default credentials.yml"
    CREDENTIALS_FILE="credentials.yml"
fi

# Check if action server is needed and running
ACTION_SERVER_STARTED_BY_ME=false
if [ "$SKIP_ACTION" = false ]; then
    log "INFO" "Checking action server on port $ACTION_PORT"
    
    if port_in_use "$ACTION_PORT"; then
        log "SUCCESS" "Action server is already running on port $ACTION_PORT"
    else
        log "INFO" "Action server is not running. Starting it now..."
        
        if [ ! -f "start_actions.sh" ]; then
            log "ERROR" "Action server script (start_actions.sh) not found"
            exit 1
        fi
        
        chmod +x ./start_actions.sh
        ./start_actions.sh > action_server.log 2>&1 &
        ACTION_SERVER_PID=$!
        ACTION_SERVER_STARTED_BY_ME=true
        
        # Wait for action server to start
        log "INFO" "Waiting for action server to start..."
        attempts=0
        while [ $attempts -lt $MAX_RETRY_ATTEMPTS ]; do
            if port_in_use "$ACTION_PORT"; then
                log "SUCCESS" "Action server started successfully on port $ACTION_PORT"
                break
            fi
            sleep $RETRY_INTERVAL
            attempts=$((attempts + 1))
            if [ $attempts -eq $MAX_RETRY_ATTEMPTS ]; then
                log "ERROR" "Failed to start action server. Check action_server.log for details."
                exit 1
            fi
            echo -n "."
        done
        echo ""  # Add a newline after the dots
        
        # Optional: Check if the action server is actually responsive
        if ! curl -s "http://localhost:$ACTION_PORT/health" > /dev/null; then
            log "WARNING" "Action server is running but may not be fully operational."
        fi
    fi
fi

# Determine server port if not manually specified
if [ "$SERVER_PORT" = "$DEFAULT_SERVER_PORT" ]; then
    SERVER_PORT=$(find_available_port "$DEFAULT_SERVER_PORT")
    
    # Ensure the selected port is not the action server port
    if [ "$SERVER_PORT" -eq "$ACTION_PORT" ]; then
        SERVER_PORT=$((SERVER_PORT + 1))
        
        # If the new port is in use, find the next available
        while port_in_use "$SERVER_PORT"; do
            SERVER_PORT=$((SERVER_PORT + 1))
        done
    fi
else
    # Verify the specified port is available
    if port_in_use "$SERVER_PORT"; then
        log "ERROR" "Specified server port $SERVER_PORT is already in use."
        exit 1
    fi
fi

# Function to clean up when this script exits
cleanup() {
    echo -e "\n"
    log "INFO" "Cleaning up..."
    
    # Only kill the action server if we started it
    if [ "$ACTION_SERVER_STARTED_BY_ME" = true ]; then
        log "INFO" "Stopping action server (PID: $ACTION_SERVER_PID)..."
        pkill -P "$ACTION_SERVER_PID" 2>/dev/null || true
        kill "$ACTION_SERVER_PID" 2>/dev/null || true
        sleep 1
        # Force kill if still running
        if ps -p "$ACTION_SERVER_PID" > /dev/null 2>&1; then
            log "WARNING" "Action server still running, forcing termination..."
            kill -9 "$ACTION_SERVER_PID" 2>/dev/null || true
        fi
    fi
    
    log "SUCCESS" "Cleanup complete."
}

# Set up trap to ensure cleanup runs on script exit
trap cleanup EXIT INT TERM

# Start Rasa with the appropriate mode
log "INFO" "Starting Rasa in $RUN_MODE mode with the following configuration:"
echo -e "${CYAN}  • Model:${NC} $(basename "$MODEL_PATH")"
echo -e "${CYAN}  • Server port:${NC} $SERVER_PORT"
echo -e "${CYAN}  • Action server port:${NC} $ACTION_PORT"
echo -e "${CYAN}  • Endpoints:${NC} $ENDPOINTS_FILE"
echo -e "${CYAN}  • Credentials:${NC} $CREDENTIALS_FILE"

log "INFO" "Loading model, this may take a moment..."

# Build the command based on run mode
RASA_CMD="rasa $RUN_MODE"

# Common parameters for all modes
RASA_PARAMS=(
  "--model" "$MODEL_PATH"
  "--endpoints" "$ENDPOINTS_FILE"
  "--credentials" "$CREDENTIALS_FILE"
  "--cors" "*"
  "--port" "$SERVER_PORT"
)

# Add mode-specific parameters
case "$RUN_MODE" in
    "shell")
        # Default shell mode parameters
        ;;
    "api"|"run")
        RASA_PARAMS+=(
            "--enable-api"
            "--log-file" "rasa_server.log"
        )
        ;;
    "debug")
        RASA_PARAMS+=(
            "--debug"
            "--enable-api"
            "--log-file" "rasa_debug.log"
        )
        ;;
esac

# Run the Rasa command
if [ "$DEBUG" = true ]; then
    log "INFO" "Running command: $RASA_CMD ${RASA_PARAMS[*]}"
fi

# Execute the command
$RASA_CMD "${RASA_PARAMS[@]}"
