#!/bin/zsh

docker-compose down
docker volume rm gitcoin-web-priv_pgdata
docker-compose up -d
echo "sleeping for 10 seconds..."
sleep 10
cd ../gitcoin-erc721
truffle migrate --reset
cd ../gitcoin-web-priv
docker-compose exec web bash -c 'cd app && python manage.py mint_all_kudos localhost /code/app/kudos/kudos.yaml'
# docker-compose exec web bash -c 'cd app && python manage.py createsuperuser --help'