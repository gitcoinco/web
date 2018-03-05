#!/bin/bash

PORT=5436
BFILE=$1
echo "DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
" | psql gitcoin -p $PORT
cat $BFILE | psql gitcoin -p $PORT

