#!/bin/bash

# =========================================================
# Google Cloud Integration for RASA
# =========================================================
# This script:
# 1. Sets up Google Cloud Storage for conversation logs
# 2. Configures Google Cloud Logging for centralized logs
# 3. Creates deployment scripts for Google Cloud Run
# =========================================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="customer-care-ai"
REGION="us-central1"  # Default region, can be changed
BUCKET_NAME="${PROJECT_NAME}-conversation-logs"
SERVICE_NAME="rasa-chatbot"

# Navigate to the script's directory
cd "$(dirname "$0")"

# Create log directory
mkdir -p logs

log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$message" | tee -a "logs/gcloud_setup.log"
}

verify_gcloud_auth() {
    log "${BLUE}🔍 Verifying Google Cloud authentication...${NC}"
    
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        local account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
        log "${GREEN}✅ Authenticated as: $account${NC}"
        return 0
    else
        log "${RED}❌ Not authenticated with Google Cloud${NC}"
        log "${YELLOW}⚠️ Please run 'gcloud auth login' first${NC}"
        return 1
    fi
}

setup_gcs_bucket() {
    log "${BLUE}🪣 Setting up Google Cloud Storage bucket...${NC}"
    
    # Check if bucket exists
    if gsutil ls -b "gs://$BUCKET_NAME" &>/dev/null; then
        log "${GREEN}✅ Bucket gs://$BUCKET_NAME already exists${NC}"
    else
        log "${YELLOW}⚠️ Creating new bucket gs://$BUCKET_NAME${NC}"
        if gsutil mb -l $REGION "gs://$BUCKET_NAME"; then
            # Set lifecycle policy to auto-delete logs older than 30 days
            echo '{
                "lifecycle": {
                    "rule": [
                        {
                            "action": {"type": "Delete"},
                            "condition": {"age": 30}
                        }
                    ]
                }
            }' > /tmp/lifecycle.json
            
            gsutil lifecycle set /tmp/lifecycle.json "gs://$BUCKET_NAME"
            rm /tmp/lifecycle.json
            
            log "${GREEN}✅ Bucket created with 30-day retention policy${NC}"
        else
            log "${RED}❌ Failed to create storage bucket${NC}"
            return 1
        fi
    fi
    
    # Create sync script for conversation logs
    cat > sync_logs_to_gcs.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
BUCKET_NAME="$1"
LOG_DIR="logs"

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: No bucket name provided"
    echo "Usage: ./sync_logs_to_gcs.sh BUCKET_NAME"
    exit 1
fi

echo "Syncing logs to gs://$BUCKET_NAME/logs/"
gsutil -m rsync -r "$LOG_DIR" "gs://$BUCKET_NAME/logs/"
echo "Sync completed at $(date)"
EOF
    
    chmod +x sync_logs_to_gcs.sh
    log "${GREEN}✅ Created log sync script: sync_logs_to_gcs.sh${NC}"
    
    return 0
}

setup_cloud_logging() {
    log "${BLUE}📊 Setting up Google Cloud Logging...${NC}"
    
    # Create logging configuration
    mkdir -p config
    cat > config/logging.conf << EOF
[loggers]
keys=root

[handlers]
keys=stream_handler,cloud_handler

[formatters]
keys=formatter

[logger_root]
level=INFO
handlers=stream_handler,cloud_handler

[handler_stream_handler]
class=StreamHandler
level=INFO
formatter=formatter
args=(sys.stderr,)

[handler_cloud_handler]
class=google.cloud.logging.handlers.CloudLoggingHandler
level=INFO
formatter=formatter
args=(client,)

[formatter_formatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
EOF
    
    # Create Python utility for cloud logging
    cat > cloud_logging_setup.py << 'EOF'
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

def setup_cloud_logging(project_name, log_name="rasa_chatbot"):
    """
    Sets up Google Cloud Logging for the application
    
    Args:
        project_name: Google Cloud project name
        log_name: Name for the log in Google Cloud
        
    Returns:
        Logger configured for Google Cloud
    """
    try:
        client = google.cloud.logging.Client(project=project_name)
        handler = CloudLoggingHandler(client, name=log_name)
        
        cloud_logger = logging.getLogger('rasa_cloud_logger')
        cloud_logger.setLevel(logging.INFO)
        cloud_logger.addHandler(handler)
        
        cloud_logger.info(f"Google Cloud Logging initialized for {project_name}")
        return cloud_logger
    except Exception as e:
        print(f"Failed to set up Google Cloud Logging: {e}")
        # Fall back to standard logging
        fallback_logger = logging.getLogger('rasa_fallback_logger')
        fallback_logger.setLevel(logging.INFO)
        fallback_logger.addHandler(logging.StreamHandler())
        return fallback_logger
EOF
    
    log "${GREEN}✅ Created Cloud Logging configuration${NC}"
    
    # Add to requirements
    echo "google-cloud-logging>=2.7.0" >> ../requirements.txt
    log "${GREEN}✅ Added Google Cloud Logging to requirements.txt${NC}"
    
    return 0
}

setup_cloud_run() {
    log "${BLUE}🚀 Creating Google Cloud Run deployment script...${NC}"
    
    cat > deploy_to_cloud_run.sh << 'EOF'
#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - override with command line arguments
PROJECT_NAME="customer-care-ai"
REGION="us-central1"
SERVICE_NAME="rasa-chatbot"
IMAGE_NAME="gcr.io/$PROJECT_NAME/$SERVICE_NAME:latest"
PORT=8080
MEMORY="2Gi"
CPU=1
MIN_INSTANCES=1
MAX_INSTANCES=5

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --project)
        PROJECT_NAME="$2"
        shift
        shift
        ;;
        --region)
        REGION="$2"
        shift
        shift
        ;;
        --service)
        SERVICE_NAME="$2"
        shift
        shift
        ;;
        --memory)
        MEMORY="$2"
        shift
        shift
        ;;
        --cpu)
        CPU="$2"
        shift
        shift
        ;;
        *)
        echo -e "${RED}Unknown option: $1${NC}"
        exit 1
        ;;
    esac
done

echo -e "${BLUE}🚀 Deploying RASA bot to Google Cloud Run${NC}"
echo -e "${YELLOW}Project: $PROJECT_NAME${NC}"
echo -e "${YELLOW}Region: $REGION${NC}"
echo -e "${YELLOW}Service: $SERVICE_NAME${NC}"

# Make sure we're in the project root
cd "$(dirname "$0")/.."

# Ensure gcloud is configured
if ! gcloud config get-value project &>/dev/null; then
    echo -e "${RED}❌ No Google Cloud project configured${NC}"
    echo -e "${YELLOW}Run 'gcloud config set project $PROJECT_NAME' first${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${BLUE}🔧 Building Docker image...${NC}"
gcloud builds submit --tag $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --port $PORT \
    --memory $MEMORY \
    --cpu $CPU \
    --min-instances $MIN_INSTANCES \
    --max-instances $MAX_INSTANCES \
    --allow-unauthenticated

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${BLUE}Service URL:${NC}"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
EOF
    
    chmod +x deploy_to_cloud_run.sh
    log "${GREEN}✅ Created Cloud Run deployment script: deploy_to_cloud_run.sh${NC}"
    
    return 0
}

main() {
    log "${BLUE}🔄 Starting Google Cloud integration setup...${NC}"
    
    # Verify authentication
    verify_gcloud_auth || return 1
    
    # Set up components
    setup_gcs_bucket
    setup_cloud_logging
    setup_cloud_run
    
    log "${GREEN}✅ Google Cloud integration setup complete${NC}"
    log "${YELLOW}→ To sync logs: ./sync_logs_to_gcs.sh $BUCKET_NAME${NC}"
    log "${YELLOW}→ To deploy to Cloud Run: ./deploy_to_cloud_run.sh${NC}"
}

# Run the main function
main
