#!/bin/bash
# render-build.sh

# Exit on error
set -o errexit

# Install any required dependencies
pip install -r requirements.txt

# Train your Rasa model (uncomment if needed)
# rasa train

# Make the entrypoint script executable
chmod +x entrypoint.sh
