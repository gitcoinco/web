#!/bin/bash

cd app
python manage.py createcachetable
python manage.py collectstatic --noinput -i other
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

