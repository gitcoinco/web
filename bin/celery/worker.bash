#!/usr/local/bin/dumb-init /bin/bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

CELERY_BEAT_ENABLED=${CELERY_BEAT_ENABLED:-''}
CELERY_APP=${CELERY_APP:-'app'}
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-'INFO'}

cd app || echo "Misconfigured Docker container..."

rm -f './celerybeat.pid'
exec celery -A "$CELERY_APP" "$SERVICE_TYPE" -l "$CELERY_LOG_LEVEL"

