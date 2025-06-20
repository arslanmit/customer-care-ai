#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print section header
print_section() {
    echo -e "\n${GREEN}==>${NC} ${YELLOW}$1${NC}"
    echo "----------------------------------------"
}

# Function to check and install system dependencies
install_system_deps() {
    print_section "Checking System Dependencies"
    
    # Check for Docker
    if ! command_exists docker; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check for Docker Compose
    if ! command_exists docker-compose; then
        echo -e "${RED}Docker Compose is not installed. Please install Docker Compose.${NC}"
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} All required system dependencies are installed"
}

# Function to set up environment
setup_environment() {
    print_section "Setting Up Environment"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file...${NC}"
        cp .env.example .env
        
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32)
        
        # Update the .env file with the generated secret key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$SECRET_KEY/" .env
            sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$SECRET_KEY/" .env
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        fi
        
        echo -e "${GREEN}✓${NC} Created .env file with generated secrets"
    else
        echo -e "${YELLOW}.env file already exists. Skipping creation.${NC}"
    fi
    
    # Create required directories
    mkdir -p data/rasa data/postgres data/redis
    
    echo -e "${GREEN}✓${NC} Environment setup complete"
}

# Function to build and start services
start_services() {
    print_section "Starting Services with Docker Compose"
    
    echo -e "${YELLOW}Pulling the latest images...${NC}"
    docker-compose -f docker-compose.prod.yml pull
    
    echo -e "\n${YELLOW}Building and starting containers...${NC}"
    docker-compose -f docker-compose.prod.yml up -d --build
    
    echo -e "\n${GREEN}✓${NC} Services are starting in the background"
    echo -e "${YELLOW}This might take a few minutes for the first run...${NC}"
    
    # Show status
    echo -e "\n${YELLOW}Checking service status...${NC}"
    docker-compose -f docker-compose.prod.yml ps
}

# Function to display post-setup information
show_post_setup_info() {
    print_section "Setup Complete!"
    
    echo -e "${GREEN}✅ Your Rasa Chatbot is now running!${NC}"
    echo ""
    echo -e "${YELLOW}Access the following services:${NC}"
    echo -e "  • Rasa API:        http://localhost:5005"
    echo -e "  • Frontend:        http://localhost:3000"
    echo -e "  • Admin Dashboard: http://localhost:3000/admin"
    echo -e "  • Prometheus:      http://localhost:9090"
    echo -e "  • Grafana:         http://localhost:3001 (admin/admin)"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo -e "  • View logs:        ${GREEN}docker-compose -f docker-compose.prod.yml logs -f${NC}"
    echo -e "  • Stop services:    ${GREEN}docker-compose -f docker-compose.prod.yml down${NC}"
    echo -e "  • Restart services: ${GREEN}docker-compose -f docker-compose.prod.yml restart${NC}"
    echo -e "  • Rebuild services: ${GREEN}docker-compose -f docker-compose.prod.yml up -d --build${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Access the admin dashboard to configure your bot"
    echo "2. Train your first model using the web interface"
    echo "3. Check the logs if you encounter any issues"
    echo ""
    echo -e "${GREEN}Happy bot building! 🚀${NC}"
}

# Main execution
main() {
    # Check if running as root
    if [ "$(id -u)" -eq 0 ]; then
        echo -e "${RED}Error: This script should not be run as root.${NC}" >&2
        exit 1
    fi
    
    # Check for required commands
    for cmd in docker docker-compose openssl; do
        if ! command_exists "$cmd"; then
            echo -e "${RED}Error: $cmd is required but not installed.${NC}" >&2
            exit 1
        fi
    done
    
    # Run setup steps
    install_system_deps
    setup_environment
    start_services
    show_post_setup_info
}

# Run the main function
main "$@"
