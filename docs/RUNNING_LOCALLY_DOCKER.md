# Running Locally with Docker (Recommended)

```shell
git clone https://github.com/gitcoinco/web.git
cd web
cp app/app/local.env app/app/.env
```

## Special instructions for Windows WSL contributors

If you are using Windows 10 Professional or Enterprise, you can download [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows). Otherwise, you will need to install and configure Docker Toolbox.

### Docker Toolbox

1. Follow the installation instructions on the [manual for installing Docker Toolbox on Windows](https://docs.docker.com/toolbox/toolbox_install_windows/).
2. WSL by default mounts your C: drive on `/mnt/c`, but Docker Toolkit instead expects it to be mounted on `/c/`. To instruct WSL to mount it in the correct location, create a config file in `/etc/wsl.conf` using WSL and enter the following:
    ```ini
    [automount]
    root = /
    options = "metadata"
    ```
3. Lastly, ensure that you are sharing the folders of your project directory to your VirtualBox VM, i.e. if your Gitcoin repository is located in `C:/Projects/web`, you will have to go to the VirtualBox UI, click on `Settings > Shared Folders`, and ensure that there is an entry with a name of `c/Projects` and a path of `C:\Projects`.

### Configure

Once Docker is installed (either via Docker Desktop for Windows or Docker Toolkit), install the Docker packages on WSL as you normally would for Ubuntu:

```shell
# Update the apt package list.
$ sudo apt-get update -y

# Install Docker's package dependencies.
$ sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

# Download and add Docker's official public PGP key.
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Verify the fingerprint.
$ sudo apt-key fingerprint 0EBFCD88

# Add the `stable` channel's Docker upstream repository.
#
# If you want to live on the edge, you can change "stable" below to "test" or
# "nightly". I highly recommend sticking with stable!
$ sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Update the apt package list (for the new apt repo).
$ sudo apt-get update -y

# Install the latest version of Docker CE.
$ sudo apt-get install -y docker-ce

# Allow your user to access the Docker CLI without needing root access.
$ sudo usermod -aG docker $USER
```

## Startup server

*Check that you have Docker and Docker-compose properly installed*
```shell
docker --version
Docker version 18.09.7, build 2d0083d

docker-compose --version
docker-compose version 1.24.1, build 4667896b
```
The above should work.

### Running in Detached mode

```shell
docker-compose up -d --build
```

The above would create a background daemon when it finished installation. It takes pretty long time, an hour or more. The good news is that it runs on its own. If you have error while running this it is likely to come from docker and docker-compose.

### Running in the foreground

```shell
docker-compose up --build
```
### Screens during building

![Installation Screenshot 1](https://github.com/gitcoinco/web/raw/master/docs/imgs/screenshot1.png "Installation screenshot")

![Installation Screenshot 2](https://github.com/gitcoinco/web/raw/master/docs/imgs/screenshot2.png "Installation screenshot")


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

![Running Screenshot 1](https://github.com/gitcoinco/web/raw/master/docs/imgs/screenshoot_server1.png "Running screenshot")

![Running Screenshot 2](https://github.com/gitcoinco/web/raw/master/docs/imgs/screenshoot_server2.png "Running screenshot")

![Running Screenshot 3](https://github.com/gitcoinco/web/raw/master/docs/imgs/screenshoot_server4.png "Running screenshot")

![Running Screenshot 4](https://github.com/gitcoinco/web/raw/master/docs/imgs/screenshoot_server5.png "Running screenshot")

For background build, Gitcoin server runs as a service and its always there. You can stop it using `kill process`, docker-compose to stop it  or other means.

*Note: Running `docker-compose logs --tail=50 -f <optional container_name>` will follow all container output in the active terminal window, while specifying a container name will follow that specific container's output. `--tail` is optional.*
Check out the [Docker Compose CLI Reference](https://docs.docker.com/compose/reference/) for more information.

## A note on performance

The Gitcoin docker containers contain serval containers for many purposes (web development, task pipeline dev, ganache for blockchain development). Because of this, the whole package can take several GB of RAM.   If all you want to do is work on the site, and you experience slowness while running Gitcoin, we recommend running these commands

> docker stop web_worker_1; docker stop web_testrpc_1; docker stop web_ipfs_1; docker stop web_chat_1

and adding this line to your .env file:

> SUPRESS_DEBUG_TOOLBAR=1

If you run `docker-compose restart web` after doing these things, you should find the performance footprint to be less.


## Integration Setup (recommended)

If you plan on using the Github or Google integration, please read the [third party integration guide](https://docs.gitcoin.co/mk_third_party_integrations/).

## Static Asset Handling (optional)

If you're testing in a staging or production style environment behind a CDN, pass the `DJANGO_STATIC_HOST` environment variable to your django web instance specifying the CDN URL.

For example:

```sh
DJANGO_STATIC_HOST='https://gitcoin.co'
```

## Initial test data

The development server is conditioned with a representative sampling of test data fixtures outlined below:

* 20ish users doing a variety things
* Bounties in various statuses - so you can get to work!
* Grants - ask some friends to support your work on Gitcoin
* A variety of Kudos for you to send to everybody hard at work on bounties
* A default superuser - usage below
    1. Go to [http://localhost:8000/_administrationeconomy/](http://localhost:8000/_administration)
    2. Login with
        * username: root
        * password: gitcoinco
    3. Poke around the database tables
    4. Click the _Impersonate User_ link,  pick any user and poke around the site

## Create Django Admin

The [initial test data](#initial-test-data) comes with a pre-configured
superuser. You can also create a new one using the following command:

```shell
docker-compose exec web python3 app/manage.py createsuperuser
```

Make sure that the services are already running. See [Startup server](#startup-server) for an example.

If the script worked correctly, you will be asked for the following information:

* username
* password
* email - optional, blank is ok

## Add a Custom ERC20 Token To your Local Gitcoin

1. [Create a django admin](https://github.com/gitcoinco/web/blob/master/docs/RUNNING_LOCALLY_DOCKER.md#create-django-admin)
2. Go to [http://localhost:8000/_administrationeconomy/token/](http://localhost:8000/_administrationeconomy/token/) and click `Add New Token`.
3. Open another tab and go to [http://tokenfactory.surge.sh](http://tokenfactory.surge.sh)
4. Mint a new token on the network of your choice.
5. Go back to your Gitcoin local tab, and enter the token.
6. Click Save
7. Congratulations, your local environment now supports your custom token!
8. You may continue administering your token over at [http://tokenfactory.surge.sh](http://tokenfactory.surge.sh).  Hint:  Maybe you should mint some? 🤔

In case `tokenfactory.surge.sh` doesn't work, you can deploy a simple `ERC20` token to a testnet using [remix](https://remix.ethereum.org).

```
// SPDX-License-Identifier:MIT
pragma solidity 0.8.10;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.4.2/contracts/token/ERC20/ERC20.sol";

contract Token is ERC20 {
    constructor() ERC20("My Test Token", "TEST") {
        _mint(msg.sender, 1_000_000 * (10 ** decimals()));
    }
}
```

## Optional: Import bounty data from web3 to your database

This can be useful if you'd like data to test with shared data:

```shell
docker-compose exec web python3 app/manage.py sync_geth rinkeby -20 99999999999
```

**Note:** using the `sync_geth` command can potentially break some of the [Initial test data](#initial-test-data) fixtures.

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

#### Docker for-mac troubleshooting


`Q: When building with docker on my mac, CPU usage is high and device is overheating what should I do?`

Problems regarding docker and high CPU usage seem to be common on mac. One community user found that going to the resources section on Docker desktop and lowering CPU cores and disk image size to minimum improves this issue.

```
For more troubleshooting tips on this problem consult the docker for-mac repo issues [https://github.com/docker/for-mac/issues?q=cpu](https://github.com/docker/for-mac/issues?q=cpu)
```

#### Fix local test issues

`Q: How can I attempt automatic remediation of eslint and isort test failures?`

```shell
make fix # npm run eslint:fix; docker-compose exec web isort -rc --atomic .;
```

#### Makefile Help

`Q: How can I see a complete list of Makefile commands and descriptions?`

Run:
```shell
make

autotranslate                  Automatically translate all untranslated entries for all LOCALES in settings.py.
build                          Build the Gitcoin Web image.
collect-static                 Collect newly added static resources from the assets directory.
compilemessages                Execute compilemessages for translations on the web container.
compress-images                Compress and optimize images throughout the repository. Requires optipng, svgo, and jpeg-recompress.
cypress                        Open cypress testing UI
eslint                         Run eslint against the project directory. Requires node, npm, and project dependencies.
fix-eslint                     Run eslint --fix against the project directory. Requires node, npm, and project dependencies.
fix                            Attempt to run all fixes against the project directory.
fix-isort                      Run isort against python files in the project directory.
fix-stylelint                  Run stylelint --fix against the project directory. Requires node, npm, and project dependencies.
fix-yapf                       Run yapf against any included or newly introduced Python code.
fresh                          Completely destroy all compose assets and start compose with a fresh build.
get_django_shell               Open a standard Django shell.
get_ipdb_shell                 Drop into the active Django shell for inspection via ipdb.
get_shell_plus                 Open a standard Django shell.
load_initial_data              Load initial development fixtures.
login                          Login to Docker Hub.
logs                           Print and actively tail the docker compose logs.
makemessages                   Execute makemessages for translations on the web container.
migrate                        Migrate the database schema with the latest unapplied migrations.
migrations                     Generate migration files for schema changes.
pgactivity                     Run pg_activivty against the local postgresql instance.
pgtop                          Run pg_top against the local postgresql instance.
push                           Push the Docker image to the Docker Hub repository.
pytest-pdb                     Run pytest with pdb support (Backend)
pytest                         Run pytest (Backend)
stylelint                      Run stylelint against the project directory. Requires node, npm, and project dependencies.
tests                          Run the full test suite.
update_fork                    Update the current fork master branch with upstream master.
update_stable                  Update the stable branch with master.

```

These are commands that you can use to play with Gitcoin web. However, they are for developer. If you want to play around some may need special docker setup. `make build` uses  docker experimental functions.

### Enable docker experimental functions

```shell
sudo nano /etc/docker/daemon.json
```

Copy and paste

```json
{
    "experimental": true 
} 
```

#### On-chain activities

`Q: Which network should I be using for local testing?`

It is recommended to use the `Rinkeby` testnet for local development testing.  You can receive some testnet eth by visiting the [Rinkeby Faucet](https://faucet.rinkeby.io/)
Alternatively, you can use the local `ganache-cli` test rpc network that ships with the docker compose stack by switching to `Localhost 8545` in Metamask.

#### Address already in use

`Q: I am receiving a "address already in use" error when attempting to run: docker-compose up`

This error can occur when you are already running a local instance of PostgreSQL or another service on any of the ports specified in the `docker-compose.yml`.  You can identify which process is currently bound to the port with: `lsof -i :<port_number> | grep LISTEN` - for example: `lsof -i :8000 | grep LISTEN` and simply `sudo kill <pid>`, substituting the PID returned from `lsof`.

#### Github Login and Google Verification

`Q: How can I enable the Github Login and/or Google verification functionality on my local docker instance?`

If you plan on using the Github and/or Google integration, please read the [third party integration guide](https://docs.gitcoin.co/mk_third_party_integrations/).

#### ipdb

`Q: what's the best way to import ipdb; ipdb.set_trace() a HTTP request via docker?`

Add `import ipdb;ipdb.set_trace()` to the method you want to inspect, you then run: `make get_ipdb_shell` to drop into the active shell for inspection.

#### Access Django Shell

`Q: How can I access the Django shell, similar to: python manage.py shell ?`

Simply run: `make get_django_shell` or `docker-compose exec web python3 app/manage.py shell`

#### Access BASH

`Q: I want to inspect or manipulate the container via bash.  How can I access the root shell of the container?`

Run: `docker-compose exec web bash`

#### I have a question about Kudos.  Is there a FAQ for that product?

Yes [click here](https://github.com/gitcoinco/web/blob/master/docs/KUDOS.md).
