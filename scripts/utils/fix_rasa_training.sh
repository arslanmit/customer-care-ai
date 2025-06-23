
show_help() {
    echo "Usage: ./fix_rasa_training.sh [options]"
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
# Usage: ./scripts/utils/fix_rasa_training.sh [options]
# Run with -h or --help for usage information

# ==========================================
# RASA Data Fix Script
# ==========================================
# Fixes YAML syntax errors in training data
# ==========================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NLU_FILE="data/nlu.yml"

echo -e "${BLUE}🔧 RASA NLU Data Fix Script${NC}"
echo -e "${YELLOW}Starting at $(date)${NC}"

if [ ! -f "$NLU_FILE" ]; then
    echo -e "${RED}❌ NLU file not found at $NLU_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating backup of NLU file...${NC}"
mkdir -p backups
timestamp=$(date +"%Y%m%d-%H%M%S")
cp "$NLU_FILE" "backups/nlu-$timestamp.yml"
echo -e "${GREEN}✅ Backup created at backups/nlu-$timestamp.yml${NC}"

echo -e "${YELLOW}Fixing YAML syntax errors...${NC}"

# Create a fixed version by extracting only correct structure
grep -v "Added by fix script" "$NLU_FILE" | grep -v "intent: change_language" | grep -v "intent: ask_datetime" | grep -v "intent: ask_info" | grep -v "intent: provide_info" | grep -v "intent: request_human_agent" | grep -v "intent: tell_joke" > "fixes/nlu_fixed.yml"

# Now add the missing intents with proper indentation
cat >> "fixes/nlu_fixed.yml" << EOF

  # Added by fix script
  - intent: change_language
    examples: |
      - Change language
      - Switch to English
      - I want to speak in Spanish
      - Can you change the language?
      - Set language to French

  - intent: ask_datetime
    examples: |
      - What time is my appointment?
      - When is my delivery scheduled?
      - What date will my order arrive?
      - What are your business hours?

  - intent: ask_info
    examples: |
      - I need some information
      - Tell me about your return policy
      - Can you explain how this works?
      - I have a question about your products

  - intent: provide_info
    examples: |
      - My email is example@email.com
      - My phone number is 555-123-4567
      - My address is 123 Main Street
      - My account number is ABC12345

  - intent: request_human_agent
    examples: |
      - I want to speak to a person
      - Connect me with a human
      - Can I talk to an agent?
      - I need to speak with someone real

  - intent: tell_joke
    examples: |
      - Tell me a joke
      - Say something funny
      - I need a laugh
      - Do you know any jokes?
EOF

echo -e "${GREEN}✅ Fixed NLU file created${NC}"

# Replace the original with the fixed version
cp "fixes/nlu_fixed.yml" "$NLU_FILE"
echo -e "${GREEN}✅ Original NLU file replaced with fixed version${NC}"

echo -e "${BLUE}💡 Now run ./train_pipeline.sh to train with the fixed data${NC}"
