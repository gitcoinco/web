#!/bin/bash

: <<'END'
Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
END

# deploy script
# assumes that gitcoin repo lives at $HOME/gitcoin
# and that gitcoin-37 is the virtualenv under which it lives

# setup
cd || echo "Cannot find directory!"
cd gitcoin/coin || echo "Cannot find coin directory!"

# Load the .env file into the local environment.
# shellcheck disable=SC2046
export $(grep -v '^#' app/app/.env | xargs)

BRANCH=$1
DISTID=$2
ISFRONTENDPUSH=$3
UPDATE_CRONTAB=${UPDATE_CRONTAB:-$4}
MIGRATE_DB=${MIGRATE_DB:-$5}
CREATE_CACHE_TABLE=${CREATE_CACHE_TABLE:-$6}

# shellcheck disable=SC1091
source ../gitcoin-37/bin/activate

# pull from git
git add .
git stash

# If no $BRANCH is specified, it will use the current one
git checkout "$BRANCH"
git pull origin "$BRANCH"

# deploy hooks
echo "- install req"
{ pip3 install -r requirements/base.txt >> /dev/null; } 2>&1

echo "- cleaning up pyc files"
find . -name \*.pyc -delete

if [ "$UPDATE_CRONTAB" ] && [ "$JOBS_NODE" ]; then
    echo "- updating crontab"
    crontab scripts/crontab
fi

cd app || echo "Cannot find app directory!"
echo "- collect static"
if [ "$ISFRONTENDPUSH" ] && [ "$JOBS_NODE" ]; then
    python3 manage.py collectstatic --noinput -i other;
fi

rm -Rf ~/gitcoin/coin/app/static/other

if [ "$MIGRATE_DB" ] && [ "$JOBS_NODE" ]; then
    echo "- db"
    python3 manage.py migrate
fi

if [ "$CREATE_CACHE_TABLE" ] && [ "$JOBS_NODE" ]; then
    echo "- creating cache table"
    python3 manage.py createcachetable
fi

# let gunicorn know its ok to restart
if ! [ "$JOBS_NODE" ]; then
    echo "- gunicorn"
    for pid in $(pgrep -fl "gunicorn: worke" | awk '{print $1}'); do
    sudo kill -1 $pid
    sleep 0.5
    done

fi

# invalidate cloudfront
if [ "$ISFRONTENDPUSH" ] && [ "$JOBS_NODE" ]; then
    if [ "$DISTID" ]; then
        cd ~/gitcoin/coin || echo "Cannot find coin directory!"; bash scripts/bustcache.bash "$DISTID"
    fi
fi

# ping google
cd ~/gitcoin/coin || echo "Cannot find coin directory!"
bash scripts/run_management_command.bash ping_google

if [ "$ENV" = "prod" ] && [ "$JOBS_NODE" ]; then
    # Handle sentry deployment
    echo "- publishing deployment information to Sentry"
    bash scripts/sentry.bash
fi
