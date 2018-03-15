# Running Locally

## With Docker

```shell
git clone https://github.com/gitcoinco/web.git
cd web
cp app/app/local.env app/app/.env
docker-compose up -d
```

Navigate to `http://0.0.0.0:8000/`.

*Note: Running `docker-compose logs --tail=50 -f <optional container_name>` will follow all container output in the active terminal window, while specifying a container name will follow that specific container's output. `--tail` is optional.*
Check out the [Docker Compose CLI Reference](https://docs.docker.com/compose/reference/) for more information.

## Without Docker

```shell
git clone https://github.com/gitcoinco/web.git
cd web/app
cp app/app/local.env app/app/.env
```

You will need to edit the `app/.env` file with your local environment variables. Look for config items that are marked `# required`.

## Setup Github OAuth2 App Integration

Navigate to: [Github - New Application](https://github.com/settings/applications/new) and enter similar values to:

* Enter Application Name: `MyGitcoinApp`
* Homepage URL: `http://localhost`
* Application description: `My Gitcoin App`
* Authorization callback URL: `http://localhost:8000/` (required)

The authorization callback URL should match your `BASE_URL` value in `local_settings.py`

Set `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `GITHUB_APP_NAME` to the returned values.

## Setup Github User Integration

Navigate to:  [Github - New Token](https://github.com/settings/tokens/new)
At minimum, select `user` scope.
Generate your token and copy it to:  `GITHUB_API_TOKEN`
Copy your Github username to:  `GITHUB_API_USER`

## Rollbar Integration

Error tracking is entirely optional and primarily for internal staging and production tracking.
If you would like to track errors of your local environment, setup an account at: [Rollbar.com](https://rollbar.com)

Once you have access to your project access tokens, you can enable rollbar error tracking for both the backend and frontend one of two ways:

* Environment Variables:
  * `ROLLBAR_CLIENT_TOKEN`
  * `ROLLBAR_SERVER_TOKEN`

* Modifying `local_settings.py` to reflect:
  * `ROLLBAR_CLIENT_TOKEN = os.environ.get('ROLLBAR_CLIENT_TOKEN', '<post_client_item>')`
  * `ROLLBAR_SERVER_TOKEN = os.environ.get('ROLLBAR_SERVER_TOKEN', '<post_server_item>')`

## Static Asset Handling

If you're testing in a staging or production style environment behind a CDN, pass the `DJANGO_STATIC_HOST` environment variable to your django web instance specifying the CDN URL.

For example:

`DJANGO_STATIC_HOST='https://gitcoin.co`

## Setup Database

PostgreSQL is the database used by this application. Here are some instructions for installing PostgreSQL on various operating systems.

[OSX](https://www.moncefbelyamani.com/how-to-install-postgresql-on-a-mac-with-homebrew-and-lunchy/)

[Windows](http://www.postgresqltutorial.com/install-postgresql/)

[Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04)

Once you have Postgres installed and running on your system, enter into a Postgres session.

```shell
psql
```

Create the database and a new privileged user.

```sql
CREATE DATABASE gitcoin;
CREATE USER gitcoin_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gitcoin TO gitcoin_user;
```

Exit Postgres session

```shell
\q
```

Update local_settings.py with the connection details.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gitcoin',
        'USER': 'gitcoin_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}
```

## Startup server

```shell
virtualenv gcoin
source gcoin/bin/activate
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
pip install -r requirements/test.txt
./manage.py migrate
./manage.py createcachetable
./manage.py get_prices
./manage.py runserver 0.0.0.0:8000
```

Navigate to `http://localhost:8000/`.

## Optional: Import bounty data from web3 to your database

This can be useful if you'd like data to test with:

```shell
./manage.py sync_geth mainnet 0 99999999999
```

## Gitcoinbot Installation Instructions

The following environment variables must be set for gitcoinbot to work correctly

```plaintext
- GITHUB_API_USER = 'gitcoinbot' ( Should correspond to [the gitcoinbot user](https://github.com/gitcoinbot))
- GITHUB_API_TOKEN = api token for gitcoinbot user (from the developer settings)
- GITCOINBOT_APP_ID = Github application id found on the settings page for [Gitcoinbot](https://github.com/apps/gitcoinbot)
- SECRET_KEYSTRING = contents of pem file from the Gitcoinbot application settings page. This is read in settings.py lines 36-38
```

Aside from these environment variables, the settings page of the gitcoin bot application must have the correct url for webhook events to post to. It should be set to `https://gitcoin.co/payload` based on urls.py line 131.

After running the migrations and deploying the gitcoin.co website, gitcoinbot will begin to receive webhook events from any repository that it is installed into. This application will then parse through the comments and respond if it is called with @gitcoinbot + registered action call.
