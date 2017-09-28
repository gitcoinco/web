#!/bin/bash

BFILE=$1
echo "DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
" | psql gitcoin -p 5436
cat $BFILE | psql gitcoin -p 5436
