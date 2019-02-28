# Running Locally without Docker

*Note: This setup method is not recommended. To ensure a consistent environment, please check out the [Docker Setup Guide](https://docs.gitcoin.co/mk_setup/).

```shell

~/$ brew install libmaxminddb automake pkg-config libtool libffi gmp python3 openssl libvips libvips-dev libvips-tools
~/$ git clone https://github.com/gitcoinco/web.git
~/$ cd web/app
~/web/app$ cp app/local.env app/.env

```

You will need to edit the `app/.env` file with your local environment variables. Look for config items that are marked `# required`.

## Configure Integrations (recommended)

If you plan on using the Github integration, please read the [third party integration guide](https://docs.gitcoin.co/mk_third_party_integrations/).

## Static Asset Handling (optional)

If you're testing in a staging or production style environment behind a CDN, pass the `DJANGO_STATIC_HOST` environment variable to your django web instance specifying the CDN URL.

For example:

`DJANGO_STATIC_HOST='https://gitcoin.co'`

## Setup Database

PostgreSQL is the database used by this application. Here are some instructions for installing PostgreSQL on various operating systems.

[OSX](https://www.moncefbelyamani.com/how-to-install-postgresql-on-a-mac-with-homebrew-and-lunchy/)

[Windows](http://www.postgresqltutorial.com/install-postgresql/)

[Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04)

Once you have Postgres installed and running on your system, enter into a Postgres session.

```shell

# For linux users
~/$ sudo -u postgres psql

# For macOS users
~/$ psql -d postgres

```

Create the database and a new privileged user.

```sql

CREATE USER gitcoin_user WITH PASSWORD 'password';
CREATE DATABASE gitcoin WITH OWNER gitcoin_user;

```

Exit Postgres session

```shell

~/$ \q

```

Update ```~/web/app/app/.env``` with the connection details, if required.

```shell

DATABASE_URL=psql://gitcoin_user:password@localhost:5432/gitcoin

```

## Setup Dependencies and Startup Server

### Setup Virtual Environment with Necessary Dependencies

```shell

~/web$ virtualenv -p python3.7 gcoin
~/web$ source gcoin/bin/activate
~/web$ pip3 install -r requirements/test.txt

```

Alternatively, if any installation errors occur:

*Note: A single error will stop the entire installation process when installing from a requirements file, this will install each module one at a time keeping installation failures isolated

```shell

~/web$ awk '!/^(-r)/' requirements/base.txt requirements/test.txt | xargs -n 1 pip3 install

```

### Startup Server

```shell

~/web/app$ ./manage.py migrate
~/web/app$ ./manage.py createcachetable
~/web/app$ ./manage.py get_prices
~/web/app$ ./manage.py runserver 0.0.0.0:8000

```

Navigate to `http://localhost:8000/`.

## Create Django Admin

```shell

~/web/app$ ./manage.py createsuperuser

```

## Optional: Import bounty data from web3 to your database

This can be useful if you'd like data to test with:


or equivalently:

```shell

~/web/app$ ./manage.py sync_geth rinkeby -20 99999999999

```
