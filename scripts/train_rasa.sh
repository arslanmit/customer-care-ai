#!/bin/bash

# Navigate to the Rasa project directory
cd "$(dirname "$0")/../backend/rasa"

# Ensure the models directory exists
mkdir -p models

echo "Training new Rasa model..."
rasa train --fixed-model-name latest_rasa_model --out models

# Check if training was successful
if [ $? -eq 0 ]; then
    echo "✅ Training completed successfully!"
    echo "Model saved to: $(pwd)/models/latest_rasa_model.tar.gz"
    
    # Ask if user wants to restart the Rasa service
    read -p "Do you want to restart the Rasa service to load the new model? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Restarting Rasa service..."
        cd "$(dirname "$0")/.."
        docker-compose restart rasa
        echo "Rasa service restarted with the new model."
    fi
else
    echo "❌ Training failed. Please check the error messages above."
    exit 1
fi
