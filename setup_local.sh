#!/bin/bash
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Customer Care AI Setup (Non-Docker)${NC}"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print("{".join(map(str, sys.version_info[:3])))')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ $PYTHON_MAJOR -lt 3 ] || { [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 8 ]; }; then
    echo -e "${YELLOW}⚠️  Python 3.8 or higher is required. Found Python $(python3 --version)${NC}"
    exit 1
fi

# Create and activate virtual environment
echo -e "${GREEN}✅ Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}✅ Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${GREEN}✅ Installing Python dependencies...${NC}
pip install -r requirements.txt

# Install development dependencies if requested
if [[ "$1" == "--dev" ]]; then
    echo -e "${GREEN}✅ Installing development dependencies...${NC}"
    pip install -r requirements-dev.txt
fi

# Install language models
echo -e "${GREEN}✅ Downloading language models...${NC}
python -m spacy download en_core_web_md
python -m spacy download es_core_news_md
python -m spacy download fr_core_news_md
python -m spacy download de_core_news_md

# Install frontend dependencies
echo -e "${GREEN}✅ Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${GREEN}✅ Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}ℹ️  Please update the .env file with your configuration${NC}"
fi

# Set up pre-commit hooks
if [ -f "$(which pre-commit)" ] && [ -f ".pre-commit-config.yaml" ]; then
    echo -e "${GREEN}✅ Setting up pre-commit hooks...${NC}"
    pre-commit install
fi

echo -e "\n${GREEN}✨ Setup complete! ✨${NC}"
echo -e "\nTo start the application, run:\n"
echo -e "${YELLOW}1. Start Redis:${NC} redis-server"
echo -e "${YELLOW}2. Start PostgreSQL:${NC} pg_ctl -D /usr/local/var/postgres start"
echo -e "${YELLOW}3. Start Rasa server:${NC} rasa run --enable-api --cors \"*\" --debug"
echo -e "${YELLOW}4. Start Rasa actions:${NC} rasa run actions --actions actions.actions"
echo -e "${YELLOW}5. Start frontend:${NC} cd frontend && npm start"
echo -e "\nAccess the application at ${GREEN}http://localhost:3000${NC}"
