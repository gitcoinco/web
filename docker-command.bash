#!/bin/bash

cd app
python manage.py collectstatic --noinput -i other
python manage.py runserver_plus 0.0.0.0:8000

