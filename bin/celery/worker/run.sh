#!/bin/bash

set -euo pipefail

celery -A taskapp worker -l INFO
