#!/bin/bash

python3 manage.py migrate

python3 manage.py loaddata app/fixtures/oauth_application.json
python3 manage.py loaddata app/fixtures/users.json
python3 manage.py loaddata app/fixtures/economy.json
python3 manage.py loaddata app/fixtures/profiles.json
python3 manage.py loaddata app/fixtures/kudos.json
python3 manage.py loaddata app/fixtures/grants.json
python3 manage.py loaddata app/fixtures/dashboard.json
python3 manage.py loaddata app/fixtures/avatar.json
python3 manage.py loaddata app/fixtures/marketing.json
python3 manage.py loaddata app/grants/fixtures/grant_types.json
