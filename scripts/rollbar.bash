#!/bin/bash

# Load the .env file into the local environment.
# shellcheck disable=SC2046
export $(grep -v '^#' app/app/.env | xargs)

REVISION=$(git rev-parse --verify HEAD)
USER=$(whoami)

echo "Submitting deployment to Rollbar - Revision: ($REVISION) - Environment: ($ENV) - User: ($USER)"
curl https://api.rollbar.com/api/1/deploy/ \
    -F access_token="$ROLLBAR_SERVER_TOKEN" \
    -F environment="$ENV" \
    -F revision="$REVISION" \
    -F local_username="$USER"
echo "Submission completed!"
