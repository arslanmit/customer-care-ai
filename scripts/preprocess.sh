#!/bin/bash
set -euo pipefail

echo "--- Pre-processing cloudrun.yaml ---"

# Cloud Build provides these as environment variables
BUILD_ID_SHORT=$(echo "$BUILD_ID" | cut -c1-8)

# Create a copy to substitute into
cp cloudrun.yaml cloudrun-processed.yaml

# Substitute placeholders and variables
sed -i.bak \
    -e "s,BUILD_ID_PLACEHOLDER,$BUILD_ID,g" \
    -e "s,BUILD_ID_SHORT_PLACEHOLDER,$BUILD_ID_SHORT,g" \
    -e "s,\${_GCR_HOSTNAME},$_GCR_HOSTNAME,g" \
    -e "s,\${PROJECT_ID},$PROJECT_ID,g" \
    -e "s,\${_SERVICE_NAME},$_SERVICE_NAME,g" \
    -e "s,\${_SERVICE_ACCOUNT},$_SERVICE_ACCOUNT,g" \
    -e "s,\${_CLOUDSQL_INSTANCE},$_CLOUDSQL_INSTANCE,g" \
    cloudrun-processed.yaml

# Clean up the backup file created by sed
rm cloudrun-processed.yaml.bak

echo "Successfully pre-processed cloudrun.yaml."
