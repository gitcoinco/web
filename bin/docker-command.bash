#!/usr/local/bin/dumb-init /bin/bash

cd app || exec echo "Docker configuration is invalid."

COLLECTSTATIC_IGNORE=${COLLECTSTATIC_IGNORE:-'other'}
CELERY_WORKERS=${CELERY_WORKERS:-'3'}

# Check whether or not the .env file exists. If not, create it.
if [ ! -f app/.env ]; then
    cp app/local.env app/.env
fi

# Enable Python dependency installation on container start/restart.
if [ ! -z "${INSTALL_REQS}" ]; then
    pip3 install -r requirements/dev.txt
fi

# Provision the Django test environment.
python manage.py createcachetable
python manage.py collectstatic --noinput -i "$COLLECTSTATIC_IGNORE" &
python manage.py migrate
python manage.py get_prices

if [[ "$ENV" == "prod" ]] || [[ "$ENV" == "stage" ]]; then
    exec gunicorn app.wsgi:application -c python:gunicorn_conf
else
    exec python3 manage.py "${WEB_RUNNER:-runserver}" "${WEB_BIND_INTERFACE:-0.0.0.0:8000}"
fi
