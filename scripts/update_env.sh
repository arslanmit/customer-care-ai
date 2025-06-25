#!/bin/bash
set -euo pipefail

echo "--- Updating Cloud Run service environment variables ---"

# Dynamically construct the actions URL
ACTIONS_URL="https://actions-${_SERVICE_NAME}-$(echo "$BUILD_ID" | cut -c1-8)-${_REGION}.run.app"

# Update the Cloud Run service with the new environment variables
gcloud run services update "$_SERVICE_NAME" \
  --region="$_REGION" \
  --project="$PROJECT_ID" \
  --platform=managed \
  --update-env-vars="PORT=8080,RASA_ENVIRONMENT=production,RASA_ACTIONS_URL=$ACTIONS_URL"

echo "Successfully updated environment variables for service: $_SERVICE_NAME."
