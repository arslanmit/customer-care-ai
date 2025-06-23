
show_help() {
    echo "Usage: ./upload_env_secrets.sh [options]"
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
# Upload all variables from a local .env file to a GitHub Environment as secrets.
# Usage: GH_ENV=production ENV_FILE=.env ./upload-env-secrets.sh
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env}"  # default .env at repo root
GH_ENV="${GH_ENV:-production}" # default environment name

if ! command -v gh >/dev/null; then
  echo "GitHub CLI (gh) not found. Install from https://cli.github.com/" >&2
  exit 1
fi

# Ensure we are inside a Git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Run this script from inside the Git repository root." >&2
  exit 1
fi

# Determine owner/repo via gh (requires gh auth login)
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

# Create environment if it does not exist
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/environments/${GH_ENV}" >/dev/null

echo "Uploading secrets from ${ENV_FILE} to environment '${GH_ENV}' in ${REPO} …"

# Process .env file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip comments and empty lines
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  
  # Extract key and value (handling values with = and #)
  key=$(echo "$line" | cut -d= -f1 | xargs)
  value=$(echo "$line" | cut -d= -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/#.*$//' | xargs)
  
  # Skip if no valid key=value pair found
  [[ -z "$key" || -z "$value" ]] && continue
  
  echo "  • $key"
  
  # Use GitHub CLI to set the secret
  echo -n "$value" | gh secret set "$key" --env "$GH_ENV" --body - || \
    echo "  ❌ Failed to set $key"
done < "$ENV_FILE"

echo "✅ All secrets uploaded to GitHub Environment '${GH_ENV}'"
