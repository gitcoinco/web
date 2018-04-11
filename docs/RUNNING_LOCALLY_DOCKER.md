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

If you plan on using the Github integration, please read the [third party integration guide](THIRD_PARTY_SETUP.md).

## Static Asset Handling (optional)

If you're testing in a staging or production style environment behind a CDN, pass the `DJANGO_STATIC_HOST` environment variable to your django web instance specifying the CDN URL.

For example:

`DJANGO_STATIC_HOST='https://gitcoin.co`

## Create Django Admin

```shell
docker-compose exec web python3 app/manage.py createsuperuser
```

## Optional: Import bounty data from web3 to your database

This can be useful if you'd like data to test with:

```shell
docker-compose exec web python3 app/manage.py sync_geth mainnet 40 99999999999
```

### FAQ

#### Running Tests

`Q: How can I run the tests locally?`

You can ensure your project will pass all Travis tests by running:

```shell
make tests # docker-compose exec web pytest -p no:ethereum; npm run eslint;
```

The above make command will run `eslint` and `pytest`.

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

#### Github Login

`Q: How can I enable the Github Login functionality on my local docker instance?`

1. Create a new OAuth app [here](https://github.com/settings/developers)
2. Set it's homepage URL to: `http://localhost:8000`
3. Set it's auth callback URL to: `http://localhost:8000/_github/callback`
4. Place the following lines in your `app/.env`:

```
GITHUB_CLIENT_ID=<COPY_FROM_GITHUB>
GITHUB_CLIENT_SECRET=<COPY_FROM_GITHUB>
```
5. Restart app via docker-compose.

#### ipdb

`Q: what's the best way to import ipdb; ipdb.set_trace() a HTTP request via docker?`

You need to run the web container with tty enabled and inspect the interactive shell.

Most people just start the stack normally, but run web outside of the standard flow. For instance, you'd want to run your service containers via something like `docker-compose up -d` then `docker-compose stop web; docker-compose run --service-ports web`

Details [here](https://github.com/docker/compose/issues/4677)



