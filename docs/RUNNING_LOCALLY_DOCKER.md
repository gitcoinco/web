# Running Locally with Docker (Recommended)

```shell
git clone https://github.com/gitcoinco/web.git
cd web
cp app/app/local.env app/app/.env
```

## Startup server

### Running in Detached mode

```shell
docker-compose up -d --build
```

### Running in the foreground

```shell
docker-compose up --build
```

### Viewing Logs

Actively follow a container's log:

```shell
docker-compose logs -f web # Or any other container name
```

View all container logs:

```shell
docker-compose logs
```

Navigate to `http://localhost:8000/`.

*Note: Running `docker-compose logs --tail=50 -f <optional container_name>` will follow all container output in the active terminal window, while specifying a container name will follow that specific container's output. `--tail` is optional.*
Check out the [Docker Compose CLI Reference](https://docs.docker.com/compose/reference/) for more information.

You will need to edit the `app/.env` file with your local environment variables. Look for config items that are marked `# required`.

## Integration Setup (recommended)

If you plan on using the Github integration, please read the [third party integration guide](https://docs.gitcoin.co/mk_third_party_integrations/).

## Static Asset Handling (optional)

If you're testing in a staging or production style environment behind a CDN, pass the `DJANGO_STATIC_HOST` environment variable to your django web instance specifying the CDN URL.

For example:

`DJANGO_STATIC_HOST='https://gitcoin.co'`

## Create Django Admin

```shell
docker-compose exec web python3 app/manage.py createsuperuser
```

## Add a Custom ERC20 Token To your Local Gitcoin

1. [Create a django admin](https://github.com/gitcoinco/web/blob/master/docs/RUNNING_LOCALLY_DOCKER.md#create-django-admin)
2. Go to [http://localhost:8000/_administrationeconomy/token/](http://localhost:8000/_administrationeconomy/token/) and click `Add New Token`.
3. Open another tab and go to [http://tokenfactory.surge.sh](http://tokenfactory.surge.sh)
4. Mint a new token on the network of ur choice.
5. Go back to your Gitcoin local tab, and enter the token.
6. Click Save
7. Congratulations, your local environment now supports your custom token!
8. You may continue administering your token over at [http://tokenfactory.surge.sh](http://tokenfactory.surge.sh).  Hint:  Maybe you should mint some? 🤔


## Optional: Import bounty data from web3 to your database

This can be useful if you'd like data to test with:


```shell
docker-compose exec web python3 app/manage.py sync_geth rinkeby -20 99999999999
```

### FAQ

#### Running Tests

`Q: How can I run the tests locally?`

You can ensure your project will pass all Travis tests by running:

```shell
make tests # docker-compose exec -e DJANGO_SETTINGS_MODULE=app.settings web pytest -p no:ethereum; npm run eslint;
```

The above make command will run `eslint` and `pytest`.

You can also run the Cypress regression tests by opening the Cypress UI by running:

```shell
make cypress
```

#### Fresh rebuild

`Q: My environment is erroring out due to missing modules/packages or postgresql errors. How can I fix it?`

```shell
make fresh # docker-compose down -v; docker-compose up -d --build;
```

#### Create superuser

`Q: How can I access the django administration login?`

```shell
make superuser # docker-compose exec web python3 app/manage.py createsuperuser
open http://localhost:8000/_administration
```

#### Fix local test issues

`Q: How can I attempt automatic remediation of eslint and isort test failures?`

```shell
make fix # npm run eslint:fix; docker-compose exec web isort -rc --atomic .;
```

#### Makefile Help

`Q: How can I see a complete list of Makefile commands and descriptions?`

```shell
make # make help
```

#### On-chain activities

`Q: Which network should I be using for local testing?`

It is recommended to use the `Rinkeby` testnet for local development testing.  You can receive some testnet eth by visiting the [Rinkeby Faucet](https://faucet.rinkeby.io/)
Alternatively, you can use the local `ganache-cli` test rpc network that ships with the docker compose stack by switching to `Localhost 8545` in Metamask.

#### Address already in use

`Q: I am receiving a "address already in use" error when attempting to run: docker-compose up`

This error can occur when you are already running a local instance of PostgreSQL or another service on any of the ports specified in the `docker-compose.yml`.  You can identify which process is currently bound to the port with: `lsof -i :<port_number> | grep LISTEN` - for example: `lsof -i :8000 | grep LISTEN` and simply `sudo kill <pid>`, substituting the PID returned from `lsof`.

#### Github Login

`Q: How can I enable the Github Login functionality on my local docker instance?`

If you plan on using the Github integration, please read the [third party integration guide](https://docs.gitcoin.co/mk_third_party_integrations/).

#### ipdb

`Q: what's the best way to import ipdb; ipdb.set_trace() a HTTP request via docker?`

Add `import ipdb;ipdb.set_trace()` to the method you want to inspect, you then run: `make get_ipdb_shell` to drop into the active shell for inspection.

#### Access Django Shell

`Q: How can I access the Django shell, similar to: python manage.py shell ?`

Simply run: `make get_django_shell` or `docker-compose exec web python app/manage.py shell`

#### Access BASH

`Q: I want to inspect or manipulate the container via bash.  How can I access the root shell of the container?`

Run: `docker-compose exec web bash`


#### I have a question about Kudos.  Is there a FAQ for that product?

Yes [click here](https://github.com/gitcoinco/web/blob/master/docs/KUDOS.md).
