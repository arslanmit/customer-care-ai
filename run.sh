#!/usr/bin/env bash
set -xeuo pipefail
trap 'echo "${RED}ERROR: Script exited unexpectedly at line $LINENO${NC}"' ERR

# Customer Care AI Unified Runner with Context7 Integration
# This script launches all core services for local development.
# Requirements: Python venv activated, Node.js, npm, Docker (for Rasa backend), Redis
# Optional: Context7 CLI for enhanced developer experience

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================="
echo -e " Customer Care AI Runner"
echo -e "=============================${NC}"

# --- Kill all related running services before startup ---
SCRIPT_PID=$$
SERVICES=("rasa" "rasa run" "rasa run actions" "rasa_sdk" )
for svc in "${SERVICES[@]}"; do
  pids=$(pgrep -f "$svc" || true)
  if [ -n "$pids" ]; then
    for pid in $pids; do
      if [ "$pid" != "$SCRIPT_PID" ]; then
        echo -e "${YELLOW}Killing process $pid for service: $svc${NC}"
        kill $pid 2>/dev/null || true
      fi
    done
  fi
done
# Also kill anything listening on 5005 or 5055 just in case
for port in 5005 5055; do
  pids=$(lsof -i :$port -sTCP:LISTEN -t || true)
  if [ -n "$pids" ]; then
    for pid in $pids; do
      if [ "$pid" != "$SCRIPT_PID" ]; then
        echo -e "${YELLOW}Killing process $pid using port $port${NC}"
        kill $pid 2>/dev/null || true
      fi
    done
  fi
done
sleep 1
echo "[CLEANUP STEP OK]"


# Check for port conflicts (Rasa: 5005, Actions: 5055)
for port in 5005 5055; do
  pid=$(lsof -i :$port -sTCP:LISTEN -t || true)
  if [ -n "$pid" ]; then
    echo -e "${RED}Port $port is still in use by process $pid.\n${NC}"
    lsof -i :$port -sTCP:LISTEN
    echo -e "${RED}Aborting. Please free the port and try again.${NC}"
    exit 1
  fi
done

# Ensure spaCy en_core_web_sm model is installed for Rasa
if ! python -m spacy validate | grep -q 'en_core_web_sm.*OK'; then
  echo -e "${YELLOW}spaCy model 'en_core_web_sm' not found. Installing...${NC}"
  python -m spacy download en_core_web_sm
fi

# Start Redis if not running
if ! pgrep -f redis-server > /dev/null; then
  echo -e "${YELLOW}Starting Redis server...${NC}"
  if command -v brew &> /dev/null; then
    brew services start redis
  else
    redis-server &
  fi
else
  echo -e "${GREEN}Redis server already running.${NC}"
fi

# Start Rasa backend (Docker recommended)
if [ -f docker-compose.yml ]; then
  if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running! Please start Docker Desktop and try again.${NC}"
    echo -e "${YELLOW}Falling back to local Rasa run...${NC}"
    if command -v rasa &> /dev/null; then
      cd backend
      rasa run --enable-api --cors "*" &
      rasa run actions &
      cd ..
    else
      echo -e "${RED}Rasa not installed. Please install or use Docker.${NC}"
      exit 1
    fi
  else
    echo -e "${BLUE}Starting Rasa backend with Docker...${NC}"
    docker-compose up -d
  fi
else
  echo -e "${YELLOW}docker-compose.yml not found. Attempting local Rasa run...${NC}"
  if command -v rasa &> /dev/null; then
    cd backend
    rasa run --enable-api --cors "*" &
    rasa run actions &
    cd ..
  else
    echo -e "${RED}Rasa not installed. Please install or use Docker.${NC}"
    exit 1
  fi
fi


# Show detailed status of all core services
sleep 2

print_service_status() {
  local name="$1"
  local port="$2"
  local pattern="$3"
  local found=0
  pids=$(pgrep -f "$pattern")
  if [ ! -z "$pids" ]; then
    found=1
    for pid in $pids; do
      addr=$(lsof -Pan -p $pid -i | grep LISTEN | awk '{print $9}' | head -n1)
      echo -e "${GREEN}$name is running${NC} (PID: $pid, Port: $port, Addr: $addr)"
    done
  fi
  if [ $found -eq 0 ]; then
    echo -e "${RED}$name is NOT running on port $port${NC}"
  fi
}

print_service_status "Redis server" 6379 "redis-server"
print_service_status "Rasa backend" 5005 "rasa run --enable-api"
print_service_status "Rasa actions server" 5055 "rasa run actions"

echo -e "${YELLOW}To stop all services, use:${NC}"
echo -e "  ${BLUE}docker-compose down${NC} (if using Docker)"
echo -e "  ${BLUE}kill $(pgrep -f 'rasa|redis|vite')${NC} (if running locally)"
