#!/usr/local/bin/dumb-init /bin/bash

cd app
# Check whether or not the .env file exists. If not, create it.
if [ ! -f app/.env ]; then
    cp app/local.env app/.env
fi

# Enable Python dependency installation on container start/restart.
if [ ! -z "${INSTALL_REQS}" ]; then
    pip3 install -r requirements/test.txt
fi

# Provision the Django test environment.
CONTAINER_NAME=$(cat /proc/self/cgroup | grep -o  -e "docker-.*.scope" | head -n 1 | sed "s/docker-\(.*\).scope/\\1/")
if [ "$CONTAINER_NAME" == "shell" ]; then
    python manage.py shell
else
    python manage.py createcachetable
    python manage.py collectstatic --noinput -i other &
    python manage.py migrate
    python manage.py get_prices
    python manage.py runserver 0.0.0.0:8000
fi

