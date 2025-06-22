#!/usr/bin/env bash
set -eo pipefail

# ---------------------------------------------------------------------------
# Customer Care AI Local Development Setup Script
# Version: 2.0.0
# Description: Sets up the Customer Care AI development environment with Rasa backend and Node.js frontend
# Context7 Integration: This script is part of the Customer Care AI project documentation
# ---------------------------------------------------------------------------

# Import Context7 documentation helper
source_context7_docs() {
    # This function would be populated by the Context7 CLI during CI/CD
    # For local development, it will fall back to local documentation
    if [ -f ".context7/docs.sh" ]; then
        source .context7/docs.sh
    else
        # Fallback documentation
        CONTEXT7_DOCS_URL="https://docs.context7.io/api/v1/docs"
        echo -e "\n${YELLOW}ℹ️  Running in local mode. For full Context7 integration, install the Context7 CLI.${NC}"
    fi
}

# Initialize Context7 documentation
source_context7_docs

# --- Install spaCy English model from local wheel if available ---
SPACY_MODEL_WHL="models/spacy/en_core_web_sm-3.7.1-py3-none-any.whl"
if [ -f "$SPACY_MODEL_WHL" ]; then
    echo -e "\n\033[1;33mInstalling spaCy model from local wheel: $SPACY_MODEL_WHL\033[0m"
    pip install "$SPACY_MODEL_WHL"
else
    echo -e "\n\033[0;31mWARNING: spaCy model wheel not found at $SPACY_MODEL_WHL. Please download it and place it there.\033[0m"
    echo "Download with: wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl -O $SPACY_MODEL_WHL"
    # Optionally, fall back to pip download here if desired
    # python -m spacy download en_core_web_sm
fi


# Colors and formatting
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'
UNDERLINE='\033[4m'

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "\n${BOLD}${UNDERLINE}$1${NC}\n"; }

# Check for required tools
check_requirements() {
    local missing=0
    local tools=("python3" "node" "npm" "git")
    
    log_step "🔍 Checking System Requirements"
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is required but not installed"
            missing=$((missing + 1))
        else
            log_success "Found $tool: $($tool --version 2>&1 | head -n 1)"
        fi
    done
    
    if [ $missing -gt 0 ]; then
        log_error "Missing $missing required tools. Please install them and try again."
        exit 1
    fi
}

# Main script execution
log_step "🚀 Customer Care AI Development Environment Setup"

# Setup environment
setup_environment() {
    log_step "🔧 Environment Setup"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log_success "Created .env file from example"
            log_warning "Please update the .env file with your configuration"
        else
            log_warning "No .env.example file found. Creating empty .env file"
            touch .env
        fi
    else
        log_success ".env file already exists"
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
}

# Setup Python backend
setup_python_backend() {
    log_step "🐍 Python Backend Setup"
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1)
    if [[ ! $PYTHON_VERSION =~ Python\s3\.[8-9]|3\.[0-9]{2,} ]]; then
        log_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        log_warning "You can install Python 3.8+ using pyenv or from python.org"
        exit 1
    fi
    log_success "Using $PYTHON_VERSION"
    
    # Install/upgrade pip and setuptools
    log_info "Upgrading pip and setuptools..."
    pip install --upgrade pip setuptools wheel
    
    # Check for Rasa installation
    if command -v rasa &> /dev/null; then
        log_success "Found Rasa: $(rasa --version | head -n 1)"
    else
        log_warning "Rasa not found. You can install it with:"
        echo "  1. Using Docker (recommended): docker-compose up -d"
        echo "  2. Manual install: pip install rasa"
        return 1
    fi
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "No requirements.txt found. Skipping Python dependencies."
    fi
    
    # Install spaCy models if needed
    if command -v python -m spacy &> /dev/null; then
        log_info "Downloading spaCy language models..."
        python -m spacy download en_core_web_md || log_warning "Failed to download en_core_web_md"
        python -m spacy download de_core_news_md || log_warning "Failed to download de_core_news_md"
    fi
}
echo -e "\n${YELLOW}📋 Setting up Node.js frontend...${NC}"

# Setup Node.js frontend
setup_node_frontend() {
    log_step "🖥️  Node.js Frontend Setup"
    
    # Check Node.js version
    NODE_VERSION=$(node --version 2>&1)
    if [[ ! $NODE_VERSION =~ v(1[4-9]|[2-9][0-9]+) ]]; then
        log_error "Node.js 14+ is required. Found: $NODE_VERSION"
        log_warning "You can install Node.js using nvm (recommended) or from nodejs.org"
        return 1
    fi
    log_success "Using Node.js $NODE_VERSION"
    
    # Check npm version
    NPM_VERSION=$(npm --version)
    log_success "Using npm $NPM_VERSION"
    
    # Install frontend dependencies
    if [ -d "frontend" ]; then
        log_info "Setting up frontend dependencies..."
        cd frontend
        
        # Check for package.json
        if [ -f "package.json" ]; then
            # Check if node_modules exists
            if [ ! -d "node_modules" ]; then
                log_info "Installing npm packages..."
                npm install --loglevel=error
                log_success "Frontend dependencies installed"
            else
                log_info "Checking for npm package updates..."
                npm update --loglevel=error
                log_success "Frontend dependencies are up to date"
            fi
            
            # Check for build step
            if [ -f "vite.config.js" ] || [ -f "vite.config.ts" ]; then
                log_info "Building frontend..."
                npm run build --if-present
            fi
        else
            log_warning "No package.json found in frontend directory"
        fi
        
        cd ..
    else
        log_warning "Frontend directory not found. Skipping frontend setup."
    fi
}

# Generate startup script
generate_startup_script() {
    log_step "🚀 Generating Startup Script"
    
    local script_name="start_dev.sh"
    cat > "$script_name" << 'EOL'
#!/usr/bin/env bash
# Auto-generated by setup_local.sh
# Start all services for Customer Care AI development

# Define colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to start a service in a new terminal window
start_service() {
    local name="$1"
    local cmd="$2"
    
    echo -e "${YELLOW}Starting $name...${NC}"
    osascript -e "tell app \"Terminal\" to do script \"echo -e '${YELLOW}$name${NC}'; $cmd; exit"
}

# Start services in separate terminal windows
start_service "Redis Server" "redis-server"
start_service "Rasa Server" "cd $(pwd) && source venv/bin/activate && cd backend && rasa run --enable-api --cors \"*\" --debug"
start_service "Rasa Actions" "cd $(pwd) && source venv/bin/activate && cd backend && rasa run actions"

# Start frontend in current terminal
if [ -d "frontend" ]; then
    echo -e "${GREEN}Starting frontend...${NC}"
    cd frontend
    if [ -f "package.json" ]; then
        if grep -q "\"dev\"" package.json; then
            npm run dev
        elif grep -q "\"start\"" package.json; then
            npm start
        else
            echo -e "${YELLOW}No dev or start script found in package.json${NC}"
            bash
        fi
    else
        echo -e "${YELLOW}No package.json found in frontend directory${NC}"
        bash
    fi
else
    echo -e "${YELLOW}Frontend directory not found. Starting shell...${NC}"
    bash
fi
EOL

    chmod +x "$script_name"
    log_success "Generated startup script: ./$script_name"
}

# Display completion message
show_completion() {
    log_step "✨ Setup Complete! ✨"
    
    echo -e "\n${GREEN}🎉 Development environment is ready!${NC}\n"
    
    echo -e "${BOLD}Next Steps:${NC}"
    echo -e "1. Review your .env file configuration"
    echo -e "2. Start the development services using: ${GREEN}./start_dev.sh${NC}"
    
    echo -e "\n${BOLD}Development URLs:${NC}"
    echo -e "- Frontend:    ${GREEN}http://localhost:3000${NC}"
    echo -e "- Rasa API:    ${GREEN}http://localhost:5005${NC}"
    echo -e "- Rasa Actions:${GREEN}http://localhost:5055${NC}"
    
    echo -e "\n${YELLOW}Note:${NC} The startup script will open multiple terminal windows for each service."
    echo -e "      You can also start services manually in separate terminals."
}

# Main execution
main() {
    check_requirements
    setup_environment
    setup_python_backend
    setup_node_frontend
    generate_startup_script
    show_completion
}

# Run the main function
main "$@"
