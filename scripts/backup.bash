#!/bin/bash

: <<'END'
Copyright (C) 2021 Gitcoin Core

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

date
BACKUPSTR=`date +"%Y%m%d-%H%M"`
MONTH=`date +"%m"`
DAY=`date +"%d"`
YEAR=`date +"%Y"`
PG_DUMP="/usr/lib/postgresql/9.6/bin/pg_dump"
export PGPASSWORD=$(cat app/app/.env | grep "DATABASE_URL" | grep -v REPLICA | awk -F "=" '{print $2}' | awk -F "@" '{print $1}' | awk -F ":" '{print $3}')
export HOST=$(cat app/app/.env | grep "DATABASE_URL" | grep -v REPLICA | awk -F "=" '{print $2}' | awk -F "@" '{print $2}' | awk -F ":" '{print $1}')
IS_PROD=$(cat app/app/.env | grep ENV | grep prod | wc -l)
if [ "$IS_PROD" -eq "1" ]; then
    # schema
    $PG_DUMP gitcoin -U gitcoin -h $HOST --schema-only | s3cmd put - s3://gitcoinbackups/$YEAR/$MONTH/$DAY/create-$BACKUPSTR-$(hostname).sql --multipart-chunk-size-mb=500

    # lite backup
    $PG_DUMP gitcoin -U gitcoin -h $HOST --data-only --exclude-table=marketing_emailevent --exclude-table=dashboard_objectview --exclude-table=marketing_stat --exclude-table=gas_gasprofile --exclude-table=marketing_githubevent --exclude-table=gas_gasguzzler --exclude-table=marketing_slackpresence | s3cmd put - s3://gitcoinbackups/$YEAR/$MONTH/$DAY/litedata-$BACKUPSTR-$(hostname).sql --multipart-chunk-size-mb=500

    # minimal backup
    $PG_DUMP gitcoin -U gitcoin -h $HOST --data-only --exclude-table=marketing_emailevent --exclude-table=dashboard_objectview --exclude-table=marketing_stat --exclude-table=gas_gasprofile --exclude-table=marketing_githubevent --exclude-table=gas_gasguzzler --exclude-table=marketing_slackpresence --exclude-table=dashboard_activity --exclude-table=marketing_leaderboardrank --exclude-table=dashboard_activity --exclude-table=perftools_jsonstore --exclude-table=pg_toast --exclude-table=dashboard_searchhistory --exclude-table=townsquare_matchranking --exclude-table=dashboard_useraction --exclude-table=grants_cartactivity --exclude-table=dashboard_profilestathistory --exclude-table=marketing_githubevent --exclude-table=django_session --exclude-table=search_searchresult | s3cmd put - s3://gitcoinbackups/$YEAR/$MONTH/$DAY/minimal-$BACKUPSTR-$(hostname).sql --multipart-chunk-size-mb=500

    # full backup
    $PG_DUMP gitcoin -U gitcoin -h $HOST | s3cmd put - s3://gitcoinbackups/$YEAR/$MONTH/$DAY/full-$BACKUPSTR-$(hostname).sql --multipart-chunk-size-mb=500


else
    echo "not prod"
fi


