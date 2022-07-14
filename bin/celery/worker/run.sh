#!/bin/bash

set -euo pipefail

cd /code/app; python3.7 manage.py celery
