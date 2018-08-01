#!/bin/bash

# Load the .env file into the local environment.
# shellcheck disable=SC2046
export $(grep -v '^#' app/app/.env | xargs)

REVISION=$(git rev-parse --verify HEAD)
USER=$(whoami)

echo "Submitting deployment to Sentry - Revision: ($REVISION) - Environment: ($ENV) - User: ($USER)"
curl https://$SENTRY_ADDRESS/api/hooks/release/builtin/$SENTRY_PROJECT/$SENTRY_TOKEN/ \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"version": "'"$REVISION"'"}'
echo "Submission completed!"
