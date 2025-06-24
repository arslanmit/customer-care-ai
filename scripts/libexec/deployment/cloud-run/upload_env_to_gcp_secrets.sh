
show_help() {
    echo "Usage: ./upload_env_to_gcp_secrets.sh [options]"
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

#!/usr/bin/env bash
# Usage: ./upload-env-to-gcp-secrets.sh .env customer-care-ai-463420

set -euo pipefail

ENV_FILE="${1:-.env}"
PROJECT_ID="${2:-customer-care-ai-463420}"

if ! command -v gcloud >/dev/null; then
  echo "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install" >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Environment file '$ENV_FILE' not found." >&2
  exit 1
fi

echo "Uploading secrets from $ENV_FILE to Google Secret Manager in project $PROJECT_ID..."

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip comments and empty lines
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

  key=$(echo "$line" | cut -d= -f1 | xargs)
  value=$(echo "$line" | cut -d= -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/#.*$//' | xargs)

  [[ -z "$key" || -z "$value" ]] && continue

  # Check if secret exists
  if gcloud secrets describe "$key" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "  • Updating secret: $key"
  else
    echo "  • Creating secret: $key"
    gcloud secrets create "$key" --replication-policy="automatic" --project="$PROJECT_ID"
  fi

  # Add new version with the value
  echo -n "$value" | gcloud secrets versions add "$key" --data-file=- --project="$PROJECT_ID"

done < "$ENV_FILE"

echo "✅ All secrets uploaded to Google Secret Manager!"
