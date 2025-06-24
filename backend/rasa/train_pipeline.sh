#!/bin/bash

# =========================================================
# Continuous Training Pipeline for RASA
# =========================================================
# This script:
# 1. Validates training data for consistency
# 2. Trains a new model with timestamp
# 3. Creates a symlink to the latest model
# 4. Logs training results
# =========================================================

# ANSI color codes for better output readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to the script's directory
cd "$(dirname "$0")"

# Check if RASA_MODEL_PATH is set
if [ -z "$RASA_MODEL_PATH" ]; then
    echo -e "${RED}❌ Error: RASA_MODEL_PATH environment variable is not set${NC}"
    echo "Please set RASA_MODEL_PATH to the desired path for saving the trained model"
    echo "Example: export RASA_MODEL_PATH=/path/to/save/model.tar.gz"
    exit 1
fi

# Create directory for the model if it doesn't exist
MODEL_DIR=$(dirname "$RASA_MODEL_PATH")
mkdir -p "$MODEL_DIR"

# Initialize log file
LOG_DIR="logs"
mkdir -p $LOG_DIR
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOG_FILE="$LOG_DIR/training_$TIMESTAMP.log"

echo -e "${BLUE}🤖 Starting RASA training pipeline at $(date)${NC}"
echo "🤖 Starting RASA training pipeline at $(date)" > $LOG_FILE

# Step 1: Data validation
echo -e "${BLUE}🔍 Validating training data...${NC}"
echo "🔍 Validating training data..." >> $LOG_FILE

if rasa data validate --fail-on-warnings >> $LOG_FILE 2>&1; then
    echo -e "${GREEN}✅ Data validation successful${NC}"
    echo "✅ Data validation successful" >> $LOG_FILE
else
    echo -e "${RED}❌ Data validation failed. Check $LOG_FILE for details${NC}"
    echo "❌ Data validation failed" >> $LOG_FILE
    exit 1
fi

# Step 2: Train the model
echo -e "${BLUE}🚂 Training new model...${NC}"
echo "🚂 Training new model..." >> $LOG_FILE

TRAINING_START=$(date +%s)

# Train the model and save to the specified location
MODEL_NAME=$(basename "$RASA_MODEL_PATH" .tar.gz)
if rasa train --fixed-model-name "$MODEL_NAME" --out "$MODEL_DIR" >> $LOG_FILE 2>&1; then
    TRAINING_END=$(date +%s)
    TRAINING_DURATION=$((TRAINING_END - TRAINING_START))
    
    echo -e "${GREEN}✅ Model training successful in $TRAINING_DURATION seconds${NC}"
    echo "✅ Model training successful in $TRAINING_DURATION seconds" >> $LOG_FILE
    
    # Verify the model was created
    if [ -f "$RASA_MODEL_PATH" ]; then
        echo -e "${GREEN}✅ Model saved to: $RASA_MODEL_PATH${NC}"
        echo "✅ Model saved to: $RASA_MODEL_PATH" >> $LOG_FILE
        
        # Create a symlink to the latest model in the models directory for backward compatibility
        mkdir -p models
        ln -sf "$RASA_MODEL_PATH" "models/$(basename "$RASA_MODEL_PATH")"
        ln -sf "$RASA_MODEL_PATH" "models/latest_model.tar.gz"
        echo -e "${GREEN}✅ Created symlinks in models/ directory${NC}"
        echo "✅ Created symlinks in models/ directory" >> $LOG_FILE
    else
        echo -e "${YELLOW}⚠️ Training completed but couldn't find the output file at $RASA_MODEL_PATH${NC}"
        echo "⚠️ Training completed but couldn't find the output file at $RASA_MODEL_PATH" >> $LOG_FILE
    fi
else
    echo -e "${RED}❌ Model training failed. Check $LOG_FILE for details${NC}"
    echo "❌ Model training failed" >> $LOG_FILE
    exit 1
fi

echo -e "${BLUE}📊 Training pipeline completed successfully at $(date)${NC}"
echo "📊 Training pipeline completed successfully at $(date)" >> $LOG_FILE

# Optional: Add notification mechanism here (email, Slack, etc.)
