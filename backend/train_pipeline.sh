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

# Train with timestamp and fixed name for easier reference
if rasa train --fixed-model-name "model-$TIMESTAMP" >> $LOG_FILE 2>&1; then
    TRAINING_END=$(date +%s)
    TRAINING_DURATION=$((TRAINING_END - TRAINING_START))
    
    echo -e "${GREEN}✅ Model training successful in $TRAINING_DURATION seconds${NC}"
    echo "✅ Model training successful in $TRAINING_DURATION seconds" >> $LOG_FILE
    
    # Find the newly created model
    NEW_MODEL=$(find models -name "model-$TIMESTAMP.tar.gz")
    
    if [ -n "$NEW_MODEL" ]; then
        # Create symlink to latest model
        ln -sf "$NEW_MODEL" models/latest_model.tar.gz
        echo -e "${GREEN}✅ Created symlink to latest model: $NEW_MODEL${NC}"
        echo "✅ Created symlink to latest model: $NEW_MODEL" >> $LOG_FILE
    else
        echo -e "${YELLOW}⚠️ Model was trained but couldn't find the output file${NC}"
        echo "⚠️ Model was trained but couldn't find the output file" >> $LOG_FILE
    fi
else
    echo -e "${RED}❌ Model training failed. Check $LOG_FILE for details${NC}"
    echo "❌ Model training failed" >> $LOG_FILE
    exit 1
fi

echo -e "${BLUE}📊 Training pipeline completed successfully at $(date)${NC}"
echo "📊 Training pipeline completed successfully at $(date)" >> $LOG_FILE

# Optional: Add notification mechanism here (email, Slack, etc.)
