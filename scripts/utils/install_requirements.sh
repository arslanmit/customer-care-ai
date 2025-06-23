
show_help() {
    echo "Usage: ./install_requirements.sh [options]"
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
# Usage: ./scripts/utils/install_requirements.sh [options]
# Run with -h or --help for usage information

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Checking for spaCy models..."
MODEL_FILES=(
    "en_core_web_md-3.7.1.tar.gz"
    "es_core_news_md-3.7.0.tar.gz"
    "fr_core_news_md-3.7.0.tar.gz"
    "de_core_news_md-3.7.0.tar.gz"
)

cd "$PROJECT_ROOT/models"

for model_file in "${MODEL_FILES[@]}"; do
    if [ -f "$model_file" ]; then
        echo "Installing $model_file..."
        pip install "$model_file"
    else
        echo "Error: $model_file not found in models/ directory."
        echo "Please run: python scripts/download_models.py"
        exit 1
    fi
done

echo "Installation complete!"
