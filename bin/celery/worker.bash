#!/usr/local/bin/dumb-init /bin/bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

CELERY_BEAT_ENABLED=${CELERY_BEAT_ENABLED:-''}
CELERY_APP=${CELERY_APP:-'app'}
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-'INFO'}
CELERY_FLOWER_INTERFACE=${CELERY_FLOWER_INTERFACE:-'0.0.0.0'}
CELERY_FLOWER_PORT=${CELERY_FLOWER_PORT:-'5555'}

cd app || echo "Misconfigured Docker container..."

rm -f './celerybeat.pid'
if [ "$SERVICE_TYPE" = "flower" ]; then
    exec flower -A "$CELERY_APP" --address="$CELERY_FLOWER_INTERFACE" --port="$CELERY_FLOWER_PORT" --loglevel="$CELERY_LOG_LEVEL"
else
    exec celery -A "$CELERY_APP" "$SERVICE_TYPE" --loglevel="$CELERY_LOG_LEVEL"
fi
