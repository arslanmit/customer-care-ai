#!/bin/bash

# Update and upgrade system packages
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    redis-server \
    postgresql \
    postgresql-contrib

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Download and install spaCy models
echo "Downloading spaCy language models..."
python -m spacy download en_core_web_md
python -m spacy download es_core_news_md
python -m spacy download fr_core_news_md
python -m spacy download de_core_news_md

# Set up environment variables
echo "Setting up environment variables..."
cat > .env << 'EOL'
# Rasa Configuration
RASA_ENVIRONMENT=development
RASA_ACTIONS_PORT=5055
RASA_ACTIONS_URL=http://localhost:5055/webhook
RASA_MODEL=./models
RASA_LOG_LEVEL=INFO

# Database Configuration
POSTGRES_USER=rasa
POSTGRES_PASSWORD=rasa123
POSTGRES_DB=rasa
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Sentry Configuration (optional)
# SENTRY_DSN=your-sentry-dsn
EOL

echo "Setup complete! To activate the virtual environment, run:"
echo "source venv/bin/activate"
echo ""
echo "Don't forget to:"
echo "1. Update the .env file with your actual configuration"
echo "2. Set up PostgreSQL database and user"
echo "3. Configure Redis if needed"
echo "4. Run 'rasa train' to train your model"
echo "5. Start the Rasa server with 'rasa run --enable-api --cors \"*\"'"
