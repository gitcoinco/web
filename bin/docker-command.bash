#!/usr/local/bin/dumb-init /bin/bash

# Load the .env file into the environment.
if [ "$ENV" == 'staging' ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' app/app/.env | xargs)
fi

# Settings
# Web
GC_WEB_WORKER=${GC_WEB_WORKER_TYPE:-runserver_plus}

# General / Overrides
FORCE_PROVISION=${FORCE_PROVISION:-'off'}
FORCE_GET_PRICES=${FORCE_GET_PRICES:-'off'}

cd app || exit 1
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

GC_WEB_OPTS="${GC_WEB_WORKER} ${GC_WEB_INTERFACE:-0.0.0.0}:${GC_WEB_PORT:-8000}"

if [ "$VSCODE_DEBUGGER_ENABLED" = "on" ]; then
    pip install ptvsd
    GC_WEB_OPTS="${GC_WEB_OPTS} --nothreading"
    echo "VSCode remote debugger enabled! This has disabled threading!"
fi

if [ "$GC_WEB_WORKER" = "runserver_plus" ]; then
    GC_WEB_OPTS="${GC_WEB_OPTS} --extra-file /code/app/app/.env --nopin --verbosity 0"
fi

# Provision the Django test environment.
if [ ! -f /provisioned ] || [ "$FORCE_PROVISION" = "on" ]; then
    echo "First run - Provisioning the local development environment..."
    if [ "$DISABLE_INITIAL_CACHETABLE" != "on" ]; then
        python manage.py createcachetable
    fi

    if [ "$DISABLE_INITIAL_COLLECTSTATIC" != "on" ]; then
        python manage.py collectstatic --noinput -i other &
    fi

    if [ "$DISABLE_INITIAL_MIGRATE" != "on" ]; then
        python manage.py migrate
    fi

    if [ "$DISABLE_INITIAL_LOADDATA" != "on" ]; then
        python manage.py loaddata initial
    fi
    date >> /provisioned
    echo "Provisioning completed!"
fi

if [ "$FORCE_GET_PRICES" = "on" ]; then
    python manage.py get_prices
fi

if [ "$KUDOS_LOCAL_SYNC" = "on" ]; then
    bash /code/scripts/sync_kudos_listener_local.bash &
    bash /code/scripts/sync_kudos_local.bash &
fi

exec python manage.py $GC_WEB_OPTS
