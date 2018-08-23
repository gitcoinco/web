#!/bin/bash

docker-compose down
docker volume rm kudos_pgdata
docker-compose up -d
echo "sleeping for 10 seconds..."
sleep 10
cd ../gitcoin-erc721
truffle migrate --reset
cd ../kudos
docker-compose exec web bash -c 'cd app && python manage.py mint_all_kudos localhost /code/app/kudos/kudos.yaml'