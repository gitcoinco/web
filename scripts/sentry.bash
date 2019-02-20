#!/bin/bash

# Load the .env file into the local environment.
# shellcheck disable=SC2046
export $(grep -v '^#' app/app/.env | xargs)

REVISION=$(git rev-parse --verify HEAD)
USER=$(whoami)

echo "Submitting deployment to Sentry - Revision: ($REVISION) - Environment: ($ENV) - User: ($USER)"
curl -v https://sentry.io/api/0/organizations/$SENTRY_ORG/releases/ \
  -X POST \
  -H 'Authorization: Bearer '"$SENTRY_TOKEN"'' \
  -H 'Content-Type: application/json' \
  -d '{"version": "'"$REVISION"'", "projects": ["'"$SENTRY_PROJECT"'"]}'
echo "Submission completed!"
