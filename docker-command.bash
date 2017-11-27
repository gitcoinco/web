#!/bin/bash

cd app
python manage.py collectstatic --noinput -i other
python manage.py runserver 0.0.0.0:8000

