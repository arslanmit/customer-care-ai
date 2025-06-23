
show_help() {
    echo "Usage: ./deploy_to_cloud_run.sh [options]"
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
# Usage: ./scripts/deployment/cloud-run/deploy_to_cloud_run.sh [options]
# Run with -h or --help for usage information

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
