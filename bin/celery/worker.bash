#!/usr/local/bin/dumb-init /bin/bash
# shellcheck disable=SC1008

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

CELERY_APP=${CELERY_APP:-'app'}
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-'INFO'}
CELERY_FLOWER_INTERFACE=${CELERY_FLOWER_INTERFACE:-'0.0.0.0'}
CELERY_FLOWER_PORT=${CELERY_FLOWER_PORT:-'5555'}
REDIS_HOST=${REDIS_HOST:-'redis'}
REDIS_PORT=${REDIS_PORT:-'6379'}
REDIS_DB=${REDIS_DB:-'0'}

cd app || { echo "Environment misconfigured! Couldn't find app directory!" >&2; exit 1; }

echo "Running Celery: $SERVICE_TYPE"

if [ "$SERVICE_TYPE" = "flower" ]; then
    exec celery -A "$CELERY_APP" flower --broker="redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB" --address="$CELERY_FLOWER_INTERFACE" --port="$CELERY_FLOWER_PORT" --loglevel="$CELERY_LOG_LEVEL"
else
    rm -f './celerybeat.pid'
    exec celery -A "$CELERY_APP" "$SERVICE_TYPE" --loglevel="$CELERY_LOG_LEVEL"
fi
