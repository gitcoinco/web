#!/bin/bash

# shellcheck disable=SC2163
while read -r line; do export "$line"; done < ./app/app/.env

REVISION=$(git rev-parse --verify HEAD)
USER=$(whoami)

echo "Submitting deployment to Rollbar - Revision: ($REVISION) - Environment: ($ENV) - User: ($USER)"
curl https://api.rollbar.com/api/1/deploy/ \
    -F access_token="$ROLLBAR_SERVER_TOKEN" \
    -F environment="$ENV" \
    -F revision="$REVISION" \
    -F local_username="$USER"
echo "Submission completed!"
