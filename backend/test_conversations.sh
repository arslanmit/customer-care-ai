#!/bin/bash

# =========================================================
# Automated Conversation Testing Framework for RASA
# =========================================================
# This script:
# 1. Runs NLU testing to validate intent recognition
# 2. Executes core tests to verify conversation flows
# 3. Generates reports for both test types
# 4. Allows custom test story selection
# =========================================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORTS_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
NLU_DATA_PATH="data/nlu.yml"
STORIES_PATH="tests/test_stories.yml"
CROSS_VALIDATION=false
MIN_SUCCESS_RATE=75  # Minimum success rate percentage to pass tests

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --nlu-only)
        NLU_ONLY=true
        shift
        ;;
        --core-only)
        CORE_ONLY=true
        shift
        ;;
        --cross-validation)
        CROSS_VALIDATION=true
        shift
        ;;
        --min-success)
        MIN_SUCCESS_RATE="$2"
        shift
        shift
        ;;
        --stories)
        STORIES_PATH="$2"
        shift
        shift
        ;;
        --help)
        echo -e "${BLUE}Automated Conversation Testing Framework for RASA${NC}"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --nlu-only          Run only NLU tests"
        echo "  --core-only         Run only Core tests"
        echo "  --cross-validation  Perform cross-validation for NLU tests"
        echo "  --min-success NUM   Minimum success rate percentage to pass tests (default: 75)"
        echo "  --stories PATH      Path to test stories file (default: tests/test_stories.yml)"
        echo "  --help              Show this help message"
        exit 0
        ;;
        *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
    esac
done

# Function to display section header
section() {
    echo
    echo -e "${BLUE}===========================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===========================${NC}"
}

# Function to check if a directory or file exists and create if needed
ensure_exists() {
    if [ ! -e "$1" ]; then
        if [ "$2" == "dir" ]; then
            mkdir -p "$1"
            echo -e "${YELLOW}Created directory: $1${NC}"
        elif [ "$2" == "file" ]; then
            touch "$1"
            echo -e "${YELLOW}Created file: $1${NC}"
        fi
    fi
}

# Function to run NLU tests
run_nlu_tests() {
    section "Running NLU Tests"
    
    # Check if NLU data file exists
    if [ ! -f "$NLU_DATA_PATH" ]; then
        echo -e "${RED}❌ NLU data file not found: $NLU_DATA_PATH${NC}"
        return 1
    fi
    
    # Create test output directory
    ensure_exists "$REPORTS_DIR/nlu" "dir"
    
    # Base command
    NLU_CMD="rasa test nlu --out $REPORTS_DIR/nlu/$TIMESTAMP"
    
    # Add cross-validation if enabled
    if [ "$CROSS_VALIDATION" = true ]; then
        NLU_CMD="$NLU_CMD --cross-validation --folds 5"
        echo -e "${YELLOW}Running with 5-fold cross-validation${NC}"
    else
        NLU_CMD="$NLU_CMD --nlu $NLU_DATA_PATH"
    fi
    
    echo -e "${YELLOW}Running command: $NLU_CMD${NC}"
    
    # Run the test command
    if eval $NLU_CMD > "$REPORTS_DIR/nlu/$TIMESTAMP-output.log" 2>&1; then
        echo -e "${GREEN}✅ NLU tests completed${NC}"
        
        # Extract and display results
        INTENT_ACCURACY=$(grep -A 5 "Intent Evaluation Results" "$REPORTS_DIR/nlu/$TIMESTAMP-output.log" | grep accuracy | awk '{print $NF}')
        if [ -n "$INTENT_ACCURACY" ]; then
            ACCURACY_PERCENT=$(echo "$INTENT_ACCURACY * 100" | bc)
            
            if (( $(echo "$ACCURACY_PERCENT >= $MIN_SUCCESS_RATE" | bc -l) )); then
                echo -e "${GREEN}✅ Intent accuracy: $ACCURACY_PERCENT% (threshold: $MIN_SUCCESS_RATE%)${NC}"
            else
                echo -e "${RED}❌ Intent accuracy: $ACCURACY_PERCENT% (below threshold: $MIN_SUCCESS_RATE%)${NC}"
                echo -e "${YELLOW}Review the detailed reports in $REPORTS_DIR/nlu/$TIMESTAMP/confmat.png${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Could not extract intent accuracy from test output${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ NLU tests failed. See log for details: $REPORTS_DIR/nlu/$TIMESTAMP-output.log${NC}"
        return 1
    fi
}

# Function to run Core tests
run_core_tests() {
    section "Running Core Tests"
    
    # Check if test stories file exists
    if [ ! -f "$STORIES_PATH" ]; then
        # Create basic test stories file if it doesn't exist
        ensure_exists $(dirname "$STORIES_PATH") "dir"
        
        echo "version: \"3.1\"

stories:
- story: Basic greeting flow test
  steps:
  - user: |
      hello
    intent: greet
  - action: utter_greet
  - user: |
      goodbye
    intent: goodbye
  - action: utter_goodbye

- story: Help request test
  steps:
  - user: |
      I need help
    intent: request_help
  - action: utter_help
" > "$STORIES_PATH"
        
        echo -e "${YELLOW}Created basic test stories file: $STORIES_PATH${NC}"
        echo -e "${YELLOW}Please customize it for your specific flows${NC}"
    fi
    
    # Create test output directory
    ensure_exists "$REPORTS_DIR/core" "dir"
    
    # Build the command
    CORE_CMD="rasa test core --stories $STORIES_PATH --out $REPORTS_DIR/core/$TIMESTAMP"
    
    echo -e "${YELLOW}Running command: $CORE_CMD${NC}"
    
    # Run the test command
    if eval $CORE_CMD > "$REPORTS_DIR/core/$TIMESTAMP-output.log" 2>&1; then
        echo -e "${GREEN}✅ Core tests completed${NC}"
        
        # Extract and display results
        STORY_SUCCESS=$(grep "Story Evaluation Results" -A 20 "$REPORTS_DIR/core/$TIMESTAMP-output.log" | grep "Success" | awk '{print $NF}' | sed 's/[^0-9]*//g')
        if [ -n "$STORY_SUCCESS" ]; then
            if (( STORY_SUCCESS >= MIN_SUCCESS_RATE )); then
                echo -e "${GREEN}✅ Story success rate: $STORY_SUCCESS% (threshold: $MIN_SUCCESS_RATE%)${NC}"
            else
                echo -e "${RED}❌ Story success rate: $STORY_SUCCESS% (below threshold: $MIN_SUCCESS_RATE%)${NC}"
                echo -e "${YELLOW}Review the detailed reports in $REPORTS_DIR/core/$TIMESTAMP/failed_stories.yml${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Could not extract success rate from test output${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Core tests failed. See log for details: $REPORTS_DIR/core/$TIMESTAMP-output.log${NC}"
        return 1
    fi
}

# Function to generate HTML report
generate_html_report() {
    section "Generating HTML Report"
    
    # Create report directory
    REPORT_PATH="$REPORTS_DIR/report-$TIMESTAMP.html"
    
    # Create HTML report
    cat > "$REPORT_PATH" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RASA Test Results - $TIMESTAMP</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .header {
            background-color: #3498db;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin: 20px 0;
            padding: 20px;
        }
        .success {
            color: #2ecc71;
        }
        .warning {
            color: #f39c12;
        }
        .error {
            color: #e74c3c;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>RASA Test Results</h1>
            <p>Generated on $(date)</p>
        </div>
        
        <div class="card">
            <h2>Summary</h2>
            <p>Test report for RASA customer care AI</p>
            <ul>
                <li><strong>Timestamp:</strong> $TIMESTAMP</li>
                <li><strong>NLU Data:</strong> $NLU_DATA_PATH</li>
                <li><strong>Test Stories:</strong> $STORIES_PATH</li>
            </ul>
        </div>
EOF

    # Add NLU section if applicable
    if [ "$CORE_ONLY" != true ] && [ -d "$REPORTS_DIR/nlu/$TIMESTAMP" ]; then
        cat >> "$REPORT_PATH" << EOF
        <div class="card">
            <h2>NLU Test Results</h2>
            <h3>Intent Classification</h3>
            <p>Confusion Matrix:</p>
            <img src="nlu/$TIMESTAMP/confmat.png" alt="Confusion Matrix">
            
            <h3>Detailed Results</h3>
            <pre>$(cat "$REPORTS_DIR/nlu/$TIMESTAMP-output.log" | grep -A 20 "Intent Evaluation")</pre>
        </div>
EOF
    fi

    # Add Core section if applicable
    if [ "$NLU_ONLY" != true ] && [ -d "$REPORTS_DIR/core/$TIMESTAMP" ]; then
        cat >> "$REPORT_PATH" << EOF
        <div class="card">
            <h2>Core Test Results</h2>
            <h3>Story Evaluation</h3>
            <pre>$(cat "$REPORTS_DIR/core/$TIMESTAMP-output.log" | grep -A 20 "Story Evaluation Results")</pre>
            
            <h3>Failed Stories</h3>
            <pre>$([ -f "$REPORTS_DIR/core/$TIMESTAMP/failed_stories.yml" ] && cat "$REPORTS_DIR/core/$TIMESTAMP/failed_stories.yml" || echo "No failed stories")</pre>
        </div>
EOF
    fi

    # Close HTML
    cat >> "$REPORT_PATH" << EOF
    </div>
</body>
</html>
EOF

    echo -e "${GREEN}✅ HTML Report generated: $REPORT_PATH${NC}"
}

# Main execution
echo -e "${BLUE}🤖 RASA Conversation Testing Framework${NC}"
echo -e "${YELLOW}Timestamp: $TIMESTAMP${NC}"

# Create main reports directory
ensure_exists "$REPORTS_DIR" "dir"

# Run tests based on flags
if [ "$CORE_ONLY" != true ]; then
    run_nlu_tests
    NLU_STATUS=$?
fi

if [ "$NLU_ONLY" != true ]; then
    run_core_tests
    CORE_STATUS=$?
fi

# Generate the HTML report
generate_html_report

# Show final result
section "Test Results Summary"

EXIT_CODE=0

if [ "$CORE_ONLY" != true ]; then
    if [ $NLU_STATUS -eq 0 ]; then
        echo -e "${GREEN}✅ NLU Tests: PASSED${NC}"
    else
        echo -e "${RED}❌ NLU Tests: FAILED${NC}"
        EXIT_CODE=1
    fi
fi

if [ "$NLU_ONLY" != true ]; then
    if [ $CORE_STATUS -eq 0 ]; then
        echo -e "${GREEN}✅ Core Tests: PASSED${NC}"
    else
        echo -e "${RED}❌ Core Tests: FAILED${NC}"
        EXIT_CODE=1
    fi
fi

echo
echo -e "${BLUE}📊 View detailed test report: $REPORT_PATH${NC}"

# Create a tests directory if needed and add a sample test stories file
ensure_exists "tests" "dir"

if [ ! -f "$STORIES_PATH" ]; then
    echo -e "${YELLOW}Creating sample test stories file...${NC}"
    echo "version: \"3.1\"

stories:
- story: Happy path
  steps:
  - user: |
      hello
    intent: greet
  - action: utter_greet
  - user: |
      I want to check my account balance
    intent: check_balance
  - action: action_check_balance
  - user: |
      thank you
    intent: thank
  - action: utter_youre_welcome
  - user: |
      goodbye
    intent: goodbye
  - action: utter_goodbye

- story: Help request
  steps:
  - user: |
      I need help
    intent: request_help
  - action: utter_help
  - user: |
      how do I make a payment?
    intent: ask_payment_method
  - action: utter_explain_payment_process
" > "$STORIES_PATH"
fi

exit $EXIT_CODE
