#!/bin/bash

# If no network is specified, use localhost
if [ -z $1 ]
then
	NETWORK=localhost
else
	NETWORK=$1
fi

ACCOUNT=$2
PRIVATE_KEY=$3

# echo $ACCOUNT
# echo $PRIVATE_KEY

docker-compose down
docker volume rm kudos_pgdata kudos_ipfsdata kudos_ipfsexport
docker-compose up -d
echo "sleeping for 10 seconds..."
sleep 10
# Enable CORS for local IPFS testing
docker-compose exec ipfs sh -c 'ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '\''["*"]'\'''
docker-compose exec ipfs sh -c 'ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '\''["PUT", "GET", "POST"]'\'''
docker-compose restart ipfs
cd ../gitcoin-erc721
truffle migrate --reset
cd ../kudos

if [ -n "$ACCOUNT" ] && [ -n $"PRIVATE_KEY" ];
then
	docker-compose exec web bash -c "cd app && python manage.py mint_all_kudos ${NETWORK} /code/app/kudos/kudos.yaml --account ${ACCOUNT} --private_key ${PRIVATE_KEY}"
else
	docker-compose exec web bash -c "cd app && python manage.py mint_all_kudos ${NETWORK} /code/app/kudos/kudos.yaml"
fi
