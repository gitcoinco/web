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
