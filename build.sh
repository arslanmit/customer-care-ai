#!/bin/bash
set -e

# Get commit SHA from environment or generate it
if [ -z "$COMMIT_SHA" ]; then
    COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "dev")
    echo "No COMMIT_SHA provided, using git SHA: $COMMIT_SHA"
fi

# Project ID based on GCR URL
PROJECT_ID="customer-care-ai-463420"
REPO_NAME="github.com/arslanmit/customer-care-ai"
IMAGE_NAME="gcr.io/$PROJECT_ID/$REPO_NAME:$COMMIT_SHA"

echo "Building Docker image: $IMAGE_NAME"

# Build the Docker image
docker build \
    -t $IMAGE_NAME \
    -f Dockerfile \
    .

# If you want to push the image to Google Container Registry
if [ "$1" == "--push" ]; then
    echo "Pushing image to Google Container Registry..."
    docker push $IMAGE_NAME
    echo "Image pushed successfully"
fi

echo "Build completed successfully"
