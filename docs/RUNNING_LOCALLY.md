# Running Locally without Docker

*Note: This setup method is not recommended. To ensure a consistent environment, please check out the [Docker Setup Guide](RUNNING_LOCALLY_DOCKER.md).

```shell
brew install libmaxminddb
git clone https://github.com/gitcoinco/web.git
cd web/app
cp app/local.env app/.env
```

You will need to edit the `app/.env` file with your local environment variables. Look for config items that are marked `# required`.

## Configure Integrations (recommended)

If you plan on using the Github integration, please read the [third party integration guide](THIRD_PARTY_SETUP.md).

## Static Asset Handling (optional)

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

## Create Django Admin

```shell
./manage.py createsuperuser
```

## Optional: Import bounty data from web3 to your database

This can be useful if you'd like data to test with:

```shell
./manage.py sync_geth mainnet 40 99999999999
```
