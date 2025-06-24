
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
echo "Installing Rasa..."
pip install rasa==3.6.21 rasa-sdk==3.6.21

echo "Installation complete!"
