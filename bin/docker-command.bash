#!/usr/local/bin/dumb-init /bin/bash
# shellcheck shell=bash disable=SC1008

cd app || exec echo "Docker configuration is invalid."

COLLECTSTATIC_IGNORE=${COLLECTSTATIC_IGNORE:-'other'}
CELERY_WORKERS=${CELERY_WORKERS:-'3'}

# Settings
# Web
WEB_WORKER=${WEB_WORKER_TYPE:-'runserver_plus'}
WEB_INTERFACE=${WEB_INTERFACE:-'0.0.0.0'}
WEB_PORT=${WEB_PORT:-'8000'}
# General / Overrides
FORCE_PROVISION=${FORCE_PROVISION:-'off'}
FORCE_GET_PRICES=${FORCE_GET_PRICES:-'off'}

# Check whether or not the .env file exists. If not, create it.
if [ ! -f app/.env ]; then
    cp app/local.env app/.env
fi

# Enable Python dependency installation on container start/restart.
if  [ ! -z "${INSTALL_REQS}" ]; then
    echo "Installing Python packages..."
    pip3 install -r ../requirements/test.txt
    echo "Python package installation completed!"
fi

echo "Environment: ($ENV)"

# Provision the Django test environment.
if [ ! -f /provisioned ] || [ "$FORCE_PROVISION" = "on" ]; then
    echo "First run - Provisioning the local development environment..."
    python manage.py createcachetable
    python manage.py collectstatic --noinput -i "$COLLECTSTATIC_IGNORE" &
    python manage.py migrate
    python manage.py loaddata initial
    date >> /provisioned
    echo "Provisioning completed!"
fi

if [ "$FORCE_GET_PRICES" = "on" ]; then
    python manage.py get_prices
fi

if [[ "$ENV" == "prod" ]] || [[ "$ENV" == "stage" ]]; then
    echo "Running Gunicorn!"
    exec gunicorn app.wsgi:application -c /code/app/gunicorn_conf.py -p /code/app/gunicorn.pid
else
    echo "Running Django Testserver!"
    exec python3 manage.py "$WEB_WORKER" "$WEB_INTERFACE":"$WEB_PORT" --extra-file /code/app/app/.env --nopin
fi
