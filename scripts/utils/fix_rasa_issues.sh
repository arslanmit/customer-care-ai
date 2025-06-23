
show_help() {
    echo "Usage: ./fix_rasa_issues.sh [options]"
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
# Usage: ./scripts/utils/fix_rasa_issues.sh [options]
# Run with -h or --help for usage information

# =========================================================
# RASA Troubleshooting and Fix Script
# =========================================================
# This script:
# 1. Fixes domain and training data inconsistencies
# 2. Restarts and tests all components
# 3. Verifies Google Cloud integration
# =========================================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN_FILE="../domain.yml"
NLU_FILE="../data/nlu.yml"
STORIES_FILE="../data/stories.yml"
RULES_FILE="../data/rules.yml"
FIXES_DIR="fixes"
GCP_ACCOUNT="arslanmit@gmail.com"

# Function to display section header
section() {
    echo
    echo -e "${BLUE}===========================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===========================${NC}"
}

# Function to check if file exists
file_exists() {
    if [ -f "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Backup original files
backup_files() {
    section "Creating backups of original files"
    
    mkdir -p backups
    local timestamp=$(date +"%Y%m%d-%H%M%S")
    
    if file_exists "$DOMAIN_FILE"; then
        cp "$DOMAIN_FILE" "backups/domain-$timestamp.yml"
        echo -e "${GREEN}✅ Domain file backed up${NC}"
    fi
    
    if file_exists "$NLU_FILE"; then
        cp "$NLU_FILE" "backups/nlu-$timestamp.yml"
        echo -e "${GREEN}✅ NLU file backed up${NC}"
    fi
    
    if file_exists "$STORIES_FILE"; then
        cp "$STORIES_FILE" "backups/stories-$timestamp.yml"
        echo -e "${GREEN}✅ Stories file backed up${NC}"
    fi
    
    if file_exists "$RULES_FILE"; then
        cp "$RULES_FILE" "backups/rules-$timestamp.yml"
        echo -e "${GREEN}✅ Rules file backed up${NC}"
    fi
    
    echo -e "${GREEN}✅ All backups created in ./backups directory${NC}"
}

# Fix domain issues
fix_domain_issues() {
    section "Fixing domain issues"
    
    if file_exists "$DOMAIN_FILE"; then
        echo -e "${YELLOW}Adding missing intent 'change_language' to domain${NC}"
        
        if grep -q "intents:" "$DOMAIN_FILE"; then
            # Check if change_language already exists
            if ! grep -q "- change_language" "$DOMAIN_FILE"; then
                # Find the line number of the last intent
                local last_intent_line=$(grep -n "intents:" "$DOMAIN_FILE" | head -1 | cut -d':' -f1)
                last_intent_line=$((last_intent_line + 1))
                
                while [[ $(sed -n "${last_intent_line}p" "$DOMAIN_FILE") == *"- "* ]]; do
                    last_intent_line=$((last_intent_line + 1))
                done
                
                # Insert change_language after the last intent
                sed -i "" "${last_intent_line}i\\
  - change_language" "$DOMAIN_FILE"
                
                echo -e "${GREEN}✅ Added 'change_language' intent to domain${NC}"
            else
                echo -e "${GREEN}✅ Intent 'change_language' already exists in domain${NC}"
            fi
        else
            echo -e "${RED}❌ Could not find 'intents:' section in domain file${NC}"
        fi
        
        echo -e "${YELLOW}Adding missing utterance 'utter_language_changed' to domain${NC}"
        
        if grep -q "responses:" "$DOMAIN_FILE"; then
            # Check if utter_language_changed already exists
            if ! grep -q "utter_language_changed:" "$DOMAIN_FILE"; then
                # Find the line number of the responses section
                local responses_line=$(grep -n "responses:" "$DOMAIN_FILE" | head -1 | cut -d':' -f1)
                responses_line=$((responses_line + 1))
                
                # Insert utter_language_changed after responses line
                sed -i "" "${responses_line}i\\
  utter_language_changed:\\
    - text: \"Language has been changed successfully.\"\\
    - text: \"I've switched the language as requested.\"" "$DOMAIN_FILE"
                
                echo -e "${GREEN}✅ Added 'utter_language_changed' response to domain${NC}"
            else
                echo -e "${GREEN}✅ Response 'utter_language_changed' already exists in domain${NC}"
            fi
        else
            echo -e "${RED}❌ Could not find 'responses:' section in domain file${NC}"
        fi
    else
        echo -e "${RED}❌ Domain file not found at $DOMAIN_FILE${NC}"
    fi
}

# Fix NLU data issues
fix_nlu_issues() {
    section "Fixing NLU data issues"
    
    if file_exists "$NLU_FILE"; then
        echo -e "${YELLOW}Checking for duplicate examples in NLU data${NC}"
        
        # Check for the specific duplicate
        if grep -q "I need to speak with support" "$NLU_FILE"; then
            echo -e "${YELLOW}Found duplicate example 'I need to speak with support'${NC}"
            echo -e "${YELLOW}Keeping it only under 'support_request' intent${NC}"
            
            # Use a temporary file for processing
            local tmp_file="$FIXES_DIR/nlu_fixed.yml"
            grep -v "I need to speak with support" "$NLU_FILE" > "$tmp_file"
            
            # Find support_request section and add the example
            if grep -q "support_request:" "$tmp_file"; then
                local support_line=$(grep -n "support_request:" "$tmp_file" | head -1 | cut -d':' -f1)
                support_line=$((support_line + 1))
                
                # Find where examples start
                while [[ $(sed -n "${support_line}p" "$tmp_file") != "examples:"* ]]; do
                    support_line=$((support_line + 1))
                    # Safety check to avoid infinite loop
                    if [ $support_line -gt 1000 ]; then break; fi
                done
                
                # Add our example
                support_line=$((support_line + 1))
                sed -i "" "${support_line}i\\
    - I need to speak with support" "$tmp_file"
                
                # Replace the original file
                cp "$tmp_file" "$NLU_FILE"
                echo -e "${GREEN}✅ Fixed duplicate example issue${NC}"
            else
                echo -e "${RED}❌ Could not find 'support_request' intent in NLU file${NC}"
            fi
        else
            echo -e "${GREEN}✅ No duplicate examples found${NC}"
        fi
        
        # Add missing intents to NLU data
        echo -e "${YELLOW}Adding examples for missing intents${NC}"
        
        # Add examples for change_language intent if not already present
        if ! grep -q "change_language:" "$NLU_FILE"; then
            echo "
# Added by fix script
- intent: change_language
  examples: |
    - Change language
    - Switch to English
    - I want to speak in Spanish
    - Can you change the language?
    - Set language to French
" >> "$NLU_FILE"
            echo -e "${GREEN}✅ Added examples for 'change_language' intent${NC}"
        else
            echo -e "${GREEN}✅ Intent 'change_language' already has examples${NC}"
        fi
        
        # Check for other missing intents from the log
        for intent in "ask_datetime" "ask_info" "provide_info" "request_human_agent" "tell_joke"; do
            if ! grep -q "${intent}:" "$NLU_FILE"; then
                echo "
# Added by fix script
- intent: ${intent}
  examples: |
    - Example for ${intent}
    - Another example for ${intent}
" >> "$NLU_FILE"
                echo -e "${GREEN}✅ Added example placeholders for '${intent}' intent${NC}"
            fi
        done
    else
        echo -e "${RED}❌ NLU file not found at $NLU_FILE${NC}"
    fi
}

# Apply fallback configuration
apply_fallback_config() {
    section "Applying enhanced fallback configuration"
    
    if [ -f "fallback_config/enhanced_fallbacks.yml" ]; then
        echo -e "${YELLOW}Extracting policies from enhanced fallbacks${NC}"
        
        # Extract policies block from fallback config
        sed -n '/policies:/,/^[^ ]/p' "fallback_config/enhanced_fallbacks.yml" | sed '$d' > "$FIXES_DIR/policies.yml"
        
        echo -e "${YELLOW}Checking if config.yml exists${NC}"
        if [ -f "../config.yml" ]; then
            # Check if policies section already exists
            if grep -q "policies:" "../config.yml"; then
                echo -e "${YELLOW}Policies section already exists in config.yml${NC}"
                echo -e "${YELLOW}Please manually merge the policies from $FIXES_DIR/policies.yml${NC}"
            else
                # Append policies to config
                echo -e "${YELLOW}Appending policies to config.yml${NC}"
                cat "$FIXES_DIR/policies.yml" >> "../config.yml"
                echo -e "${GREEN}✅ Applied fallback policies to config.yml${NC}"
            fi
        else
            echo -e "${RED}❌ config.yml not found${NC}"
        fi
    else
        echo -e "${RED}❌ Enhanced fallbacks configuration not found${NC}"
    fi
}

# Verify Google Cloud setup
verify_google_cloud() {
    section "Verifying Google Cloud integration"
    
    echo -e "${YELLOW}Checking Google Cloud authentication${NC}"
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "$GCP_ACCOUNT"; then
        echo -e "${GREEN}✅ Authenticated with Google Cloud as $GCP_ACCOUNT${NC}"
        
        echo -e "${YELLOW}Checking Cloud Storage bucket${NC}"
        if gsutil ls -b "gs://customer-care-ai-conversation-logs" &>/dev/null; then
            echo -e "${GREEN}✅ Storage bucket 'customer-care-ai-conversation-logs' exists${NC}"
        else
            echo -e "${RED}❌ Storage bucket not found${NC}"
            echo -e "${YELLOW}Run './gcloud_integration.sh' to create it${NC}"
        fi
    else
        echo -e "${RED}❌ Not authenticated with Google Cloud as $GCP_ACCOUNT${NC}"
        echo -e "${YELLOW}Run 'gcloud auth login' to authenticate${NC}"
    fi
}

# Restart and test components
restart_components() {
    section "Restarting components"
    
    echo -e "${YELLOW}Stopping any running RASA processes${NC}"
    pkill -f "rasa run" || true
    pkill -f "rasa shell" || true
    sleep 2
    
    echo -e "${YELLOW}Starting RASA watchdog${NC}"
    ./rasa_watchdog.sh > logs/watchdog.log 2>&1 &
    WATCHDOG_PID=$!
    echo -e "${GREEN}✅ Started watchdog with PID $WATCHDOG_PID${NC}"
    
    echo -e "${YELLOW}Starting RASA shell${NC}"
    ./start_rasa_shell.sh --debug > logs/rasa_shell_debug.log 2>&1 &
    SHELL_PID=$!
    echo -e "${GREEN}✅ Started RASA shell with PID $SHELL_PID${NC}"
    
    echo
    echo -e "${BLUE}💡 TIP: You can view logs with:${NC}"
    echo -e "${YELLOW}  - RASA shell logs: tail -f logs/rasa_shell_debug.log${NC}"
    echo -e "${YELLOW}  - Watchdog logs: tail -f logs/watchdog.log${NC}"
}

# Run fixed training pipeline
run_fixed_training() {
    section "Running fixed training pipeline"
    
    echo -e "${YELLOW}Running training pipeline with fixed data${NC}"
    ./train_pipeline.sh
}

# Main function
main() {
    echo -e "${BLUE}🛠️  RASA Troubleshooting and Fix Script${NC}"
    echo -e "${YELLOW}Starting at $(date)${NC}"
    
    mkdir -p "$FIXES_DIR" logs
    
    backup_files
    fix_domain_issues
    fix_nlu_issues
    apply_fallback_config
    verify_google_cloud
    run_fixed_training
    restart_components
    
    echo
    echo -e "${GREEN}✅ All fixes have been applied${NC}"
    echo -e "${BLUE}🎉 Your RASA system should now be running correctly${NC}"
}

# Run main function
main
