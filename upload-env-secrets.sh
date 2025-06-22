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
# wait_timer=0 disables required wait timer (optional)
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/environments/${GH_ENV}" >/dev/null

echo "Uploading secrets from ${ENV_FILE} to environment '${GH_ENV}' in ${REPO} …"

# Iterate over lines VAR=VALUE (skip comments/blanks)
while IFS='=' read -r key value || [[ -n "$key" ]]; do
  [[ -z "$key" || "$key" == \#* ]] && continue
  echo "  • $key"
  gh secret set "$key" --env "$GH_ENV" --body "${value}"
done < <(grep -v '^#' "$ENV_FILE" | grep -v '^\s*$')

echo "Done ✅"
