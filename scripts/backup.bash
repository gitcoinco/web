date
BACKUPSTR=`date +"%Y%m%d"`
MONTH=`date +"%m"`
DAY=`date +"%d"`
YEAR=`date +"%Y"`
sudo runuser -l postgres -c '/usr/bin/pg_dump gitcoin' > /tmp/$BACKUPSTR.sql
s3cmd put /tmp/$BACKUPSTR.sql s3://gitcoinbackups/$YEAR/$MONTH/$DAY/$BACKUPSTR-$(hostname).sql
rm /tmp/$BACKUPSTR.sql

