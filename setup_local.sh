#!/usr/bin/env bash
set -e

# ---------------------------------------------------------------------------
# Customer Care AI local setup script (Supabase-first, non-Docker)
# Idempotent: safely skips steps if already completed.
# ---------------------------------------------------------------------------

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Customer Care AI one-time setup${NC}"

# 1. Validate Python version (>=3.8)
if ! python3 - <<'PY' ; then exit 1; fi
import sys, re
major, minor = sys.version_info[:2]
print(f'Using Python {major}.{minor}')
if (major, minor) < (3, 8):
    print('Python 3.8+ required', file=sys.stderr)
    sys.exit(1)
PY

# 2. Create / activate venv
if [ ! -d "venv" ]; then
  echo -e "${GREEN}✅ Creating Python virtual environment...${NC}"
  python3 -m venv venv
fi
source venv/bin/activate

# 3. Ensure pip up to date
python -m pip install --quiet --upgrade pip

# 4. Backend Python deps
if ! pip show rasa >/dev/null 2>&1; then
  echo -e "${GREEN}✅ Installing backend requirements...${NC}"
  pip install --quiet -r requirements.txt
fi

# Optional dev dependencies
if [[ "$1" == "--dev" ]] && [ -f requirements-dev.txt ]; then
  echo -e "${GREEN}✅ Installing development requirements...${NC}"
  pip install --quiet -r requirements-dev.txt
fi

# 5. spaCy language models (install only if missing)
MODELS=(en_core_web_md es_core_news_md fr_core_news_md de_core_news_md)
for model in "${MODELS[@]}"; do
  if ! python -m spacy validate | grep -q "^$model"; then
    echo -e "${GREEN}✅ Downloading language model $model...${NC}"
    python -m spacy download "$model"
  fi
done

# 6. Frontend dependencies
pushd frontend >/dev/null
if [ ! -d node_modules ]; then
  echo -e "${GREEN}✅ Installing frontend npm packages...${NC}"
  npm install --silent
fi
popd >/dev/null

# 7. .env management
if [ ! -f .env ]; then
  echo -e "${GREEN}✅ Creating .env from example...${NC}"
  cp .env.example .env
fi

# shellcheck disable=SC1091
source .env || true
if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_KEY" || -z "$VITE_SUPABASE_URL" || -z "$VITE_SUPABASE_KEY" ]]; then
  echo -e "${YELLOW}⚠️  Supabase environment variables are missing in .env. Please update them before running the app.${NC}"
fi

# 8. pre-commit hooks
if command -v pre-commit >/dev/null 2>&1 && [ -f .pre-commit-config.yaml ]; then
  echo -e "${GREEN}✅ Installing Git pre-commit hooks...${NC}"
  pre-commit install
fi

# 9. Done
cat << EOF
${GREEN}✨ Setup complete! ✨${NC}

Next steps:
  ${YELLOW}1.${NC} Start Rasa backend:    rasa run --enable-api --cors "*" --debug
  ${YELLOW}2.${NC} Start Rasa actions:    rasa run actions --actions actions.actions
  ${YELLOW}3.${NC} Start frontend:        cd frontend && npm start

Open the app at ${GREEN}http://localhost:3000${NC}
EOF
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
echo -e "${YELLOW}2. Ensure SUPABASE_DB_URL and SUPABASE_KEY are set in .env (Supabase Postgres is used)"
echo -e "${YELLOW}3. Start Rasa server:${NC} rasa run --enable-api --cors \"*\" --debug"
echo -e "${YELLOW}4. Start Rasa actions:${NC} rasa run actions --actions actions.actions"
echo -e "${YELLOW}5. Start frontend:${NC} cd frontend && npm start"
echo -e "\nAccess the application at ${GREEN}http://localhost:3000${NC}"
