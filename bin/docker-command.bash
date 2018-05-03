#!/usr/local/bin/dumb-init /bin/bash

# Settings
# Web
WEB_WORKER=${WEB_WORKER_TYPE:-'runserver_plus'}
WEB_INTERFACE=${WEB_INTERFACE:-'0.0.0.0'}
WEB_PORT=${WEB_PORT:-'8000'}
# General / Overrides
FORCE_PROVISION=${FORCE_PROVISION:-'off'}

cd app
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

# Provision the Django test environment.
if [ ! -f /provisioned ] || [ "$FORCE_PROVISION" = "on" ]; then
    echo "First run - Provisioning the local development environment..."
    python manage.py createcachetable
    python manage.py collectstatic --noinput -i other &
    python manage.py migrate
    python manage.py get_prices
    date >> /provisioned
    echo "Provisioning completed!"
fi

python manage.py "$WEB_WORKER" "$WEB_INTERFACE":"$WEB_PORT" --extra-file /code/app/app/.env --nopin
