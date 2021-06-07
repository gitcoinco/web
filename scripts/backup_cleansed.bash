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
BACKUPSTR=$(date +"%Y%m%d")
MONTH=$(date +"%m")
DAY=$(date +"%d")
YEAR=$(date +"%Y")

# remove emails, keys from tips table
sudo runuser -l postgres -c '/usr/bin/pg_dump gitcoin' | sed 's/[\.a-zA-z0-9]*\@/xxxxx@/g' | sed 's/\@[\.a-zA-z0-9]*/@DOMAIN.TLD/g' | sed 's/key=[\.a-zA-z0-9]*/key=XXXX/g' > /tmp/$BACKUPSTR.sql
s3cmd put /tmp/$BACKUPSTR.sql s3://gitcoinbackups/$YEAR/$MONTH/$DAY/$BACKUPSTR-$(hostname)-cleansed.sql
rm /tmp/$BACKUPSTR.sql

