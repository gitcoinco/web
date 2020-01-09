#!/bin/bash

set -euo pipefail

cd /code/app; python3 manage.py celery
