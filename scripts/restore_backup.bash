#!/bin/bash

#apt-get update
#apt-get install postgresql-client -y

BFILE=$1
echo "DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
" | psql postgres -p 5432 -h db -U postgres
cat $BFILE | psql postgres -p 5432 -h db -U postgres

