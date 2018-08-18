#!/usr/bin/dumb-init /bin/bash
export PGPASSWORD=${POSTGRES_PASSWORD}
export PSQL_HOST=${POSTGRES_HOST}
export PSQL_PORT="${POSTGRES_PORT:-5432}"
export PSQL_USER=${POSTGRES_USER}
export PSQL_DB=${POSTGRES_DATABASE}
export ENV="${ENV:-manual}"
export JOB_ID="${JOB_ID:-NA}"
export DB_BACKUPS_BUCKET="${DB_BACKUPS_BUCKET:-gitcoinbackups}"
export AWS_DEFAULT_REGION="${AWS_REGION:-us-west-2}"
export AWS_ACCESS_KEY_ID=$S3_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$S3_SECRET_ACCESS_KEY
export GZIP="${GZIP:-on}"
export DB_BACKUP_CLEANSE="${DB_BACKUP_CLEANSE:-off}"

"${JOB_TYPE:?You must set the JOB_TYPE environment variable}"

JOB_DESC="Job: ($JOB_ID) - Type: ($JOB_TYPE) - Environment: ($ENV) -"

echo "$JOB_DESC Started!"
echo "$PSQL_HOST"
date
MONTH=$(date +"%m")
DAY=$(date +"%d")
YEAR=$(date +"%Y")

# PSQL_HOST_OPTS="-h $PSQL_HOST -p $PSQL_PORT -U $PSQL_USER"
S3_DB_BACKUP_PATH="s3://$DB_BACKUPS_BUCKET/$ENV/$YEAR/$MONTH/$DAY"

gunzip_dump () {
    # If GZIP is enabled, compress dump.sql file.
    if [ "$GZIP" = "on" ]; then
        echo "GZip started!"
        gzip -f dump.sql > dump.sql.gz
        echo "GZip completed!"
    fi
}

backup_db () {
    echo "Database backup started - Database: ($PSQL_DB)"
    # If DB_BACKUP_CLEANSE is enabled,
    if [ "$DB_BACKUP_CLEANSE" = "on" ]; then
        DUMP_OUT="| sed 's/[\\.a-zA-z0-9]*\\@/xxxxx@/g' | sed 's/\\@[\\.a-zA-z0-9]*/@DOMAIN.TLD/g' | sed 's/key=[\\.a-zA-z0-9]*/key=XXXX/g' > dump.sql"
    else
        DUMP_OUT="--file=dump.sql"
    fi
    pg_dump "$PSQL_DB" -h "$PSQL_HOST" -p "$PSQL_PORT" -U "$PSQL_USER" "$DUMP_OUT"
    echo "Backup completed! - Database: ($PSQL_DB)"
    gunzip_dump
}

if [ "$JOB_TYPE" = "db-backup" ]; then
    backup_db
    echo "Upload started!"
    aws s3 cp dump.sql.gz "$S3_DB_BACKUP_PATH"/"$PSQL_DB".sql.gz
    echo "Upload completed!"
elif [ "$JOB_TYPE" = "db-backup-all" ]; then
    echo "Dump started - All Databases"
    pg_dumpall "$PSQL_DB" -h "$PSQL_HOST" -p "$PSQL_PORT" --file=dump.sql
    echo "Dump completed! - All Databases"
    gunzip_dump
    echo "Upload started!"
    aws s3 cp dump.sql.gz s3://"$S3_DB_BACKUP_PATH"/all.sql.gz
    echo "Upload completed!"
elif [ "$JOB_TYPE" = "db-restore" ]; then
    echo "Database restore started - Database: ($PSQL_DB)"
    RESTORATION_KEY=${DB_RESTORATION_KEY:-'stage/latest.sql.gz'}
    # Example: RESTORATION_KEY=stage/2018/04/05/gitcoin.sql.gz
    aws s3 cp s3://"$DB_BACKUPS_BUCKET"/"$RESTORATION_KEY" dump.sql.gz || exit 2
    gunzip -c dump.sql.gz | psql "$POSTGRES_HOST_OPTS" "$POSTGRES_DATABASE"
    echo "Restore from S3 completed!"
elif [ "$JOB_TYPE" = "cf-bust" ]; then
    "${CF_DISTIBUTION_ID:?You must set the CF_DISTIBUTION_ID environment variable}"
    echo "Cloudfront cache busting started - Distribution ID: ($CF_DISTIBUTION_ID)"
    aws cloudfront create-invalidation --distribution-id "$CF_DISTIBUTION_ID" --invalidation-batch="Paths={Quantity=1,Items=["/*"]},CallerReference=$(date)"
    echo "Cloudfront cache busting completed - Distribution ID: ($CF_DISTIBUTION_ID)"
else
    echo "No recognized job type specified!"
fi
echo "$JOB_DESC Completed!"
