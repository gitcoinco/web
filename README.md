<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/263e3q1M2Y2r3L1X3c2y/helmet.png'/>

# Gitcoin

Gitcoin pushes Open Source Forward. Learn more at [https://gitcoin.co](https://gitcoin.co)

# web repo

[![Build Status](https://travis-ci.org/gitcoinco/web.svg?branch=master)](https://travis-ci.org/gitcoinco/web)
[![codecov](https://codecov.io/gh/gitcoinco/web/branch/master/graph/badge.svg)](https://codecov.io/gh/gitcoinco/web)
[![Waffle.io - Columns and their card count](https://badge.waffle.io/gitcoinco/web.svg?columns=all)](https://waffle.io/gitcoinco/web)

This is the website that is live at gitcoin.co

## How to interact with this repo

### On Github

[Star](https://github.com/gitcoinco/web/stargazers) and [watch](https://github.com/gitcoinco/web/watchers) this github repository to stay up to date, we're pushing new code several times per week!

Also,

* want to become a contributor ? Checkout our [guidelines](./docs/CONTRIBUTING.md).
* [check out the gitcoinco organization-wide repo](https://github.com/gitcoinco/gitcoinco).
* check out the open issues list, especially the [discussion](https://github.com/gitcoinco/web/issues?q=is%3Aissue+is%3Aopen+label%3Adiscussion) label and [easy-pickings](https://github.com/gitcoinco/web/issues?q=is%3Aissue+is%3Aopen+label%3Aeasy-pickings).

### On Gitcoin

<a href="https://gitcoin.co/explorer/?q=https://github.com/gitcoinco/web">
    <img src='https://gitcoin.co/funding/embed?repo=https://github.com/gitcoinco&v=2' />
</a>

## What

Functionally, the app has several key features:

* Smart Contracts -- Where funded issues are stored and indexed.
* Brochureware -- Describes the project.
* Funded Issue Explorer -- A searchable index of all of the work available in the system.
* Funded Issue Submission / Acceptance flow -- Interface between the application and web3.

[More about how/why to interact with web3 here](https://gitcoin.co/web3).

Technically, the system is architected:

* __Web3__ The main source of truth for the system is the Ethereum blockchain. Check out the [smart contracts](https://github.com/gitcoinco/smart_contracts).
* __Web2__ This part of the app is built with Python, Django, Postgres, and a handful of other tools that are common in the web2 ecosystem.
* __Web 3 Bridge__ This is the bridge between web3 and the rest of the application. Mostly built in javascript(web3js) and python(web3py).
* __Brochureware__ Just a nice little landing page telling folks what the Gitcoin project is.

# HTTPS API

Gitcoin provides a simple HTTPS API to access data without having to run your own Ethereum node. The API is live at https://gitcoin.co/api/v0.1

### Datatypes

Beyond simple datatypes like `string` or `integer` the API returns datatypes like dates that are serialized in a very specific fashion.

|  Datatype          |    Description                                            | Example
|--------------------|-----------------------------------------------------------| --------------------------------------------------------------------------------------|
| `date_time`        | Date and time represented in ISO 8601                     | `2017-09-24T18:59:53.964344Z`|
| `ethereum_address` | An ethereum token address with the leading `0x`           | `0x636f3093258412b96c43bef3663f1b853253ec59` |
| `token_type`       | The type of token offered as a reward. Ex: `ETH` or `GIT` | `ETH`                                        |

### `bounties`

The bounties endpoint provides a listing of bounties and their current status. There are two endpoints that access bounties:

- `https://gitcoin.co/api/v0.1/bounties` - Returns a list of bounties
- `https://gitcoin.co/api/v0.1/bounties/<bountyId>` - Returns a single bounty by ID.

#### Fields

| Field Key          |  Datatype          | Description                                                       |
|--------------------|--------------------|-------------------------------------------------------------------|
| `url`              | `string`           | URL for this specific bounty Ex: api/v0.1/bounties/9              |
| `created_on`       | `date_time`        | Creation timestamp                                                |
| `modified_on`      | `date_time`        | Last modified timestamp                                           |
| `title`            | `string`           | Title of the bounty                                               |
| `web3_created`     | `date_time`        | Creation timestamp for the transaction that holds this bounty     |
| `value_in_token`   | `integer`          | Amount of tokens rewarded for bounty                              |
| `token_name`       | `token_type`       | Type of token. Ex: `ETH`, `GIT`                                   |
| `token_address`    | `ethereum_address` | Address where the tokens are located                              |
| `bounty_type`      | `string`           | Type of bounty. Ex: `Bug`, `Feature`, `Security`                  |
| `project_length`   | `string`           | Relative length of project Ex: `Hours`, `Days`, `Weeks`, `Months` |
| `experience_level` | `string`           | Recommended experience level                                      |
| `github_url`       | `string`           | URL on GitHub where you can find the bounty description           |
| `current_bounty`   | `boolean`          | Whether this bounty is the most current revision one or not       |
| `expires_date`     | `date_time`        | Date before which the bounty must be compelted                    |
| `raw_data`         | `array`            | Raw contract data, see the example below for more information     |
| `value_in_eth`     | `integer`          | Value of the bounty in Ethereum                                   |
| `value_in_usdt`    | `float`            | Approximation of current value in USD                             |
| `now`              | `date_time`        | Current date_time on the server                                   |

**Current Status**

| Field Key |  Datatype |  Description                                                                                                                                                                                               |
|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `is_open` | `boolean` | True if the bounty has not been completed|
| `status`  | `string`  | Current status enum: (`open`, The bounty was created), (`started`, The bounty was started) (`submitted`, Someone submitted work for the bounty) (`done`, Someone fulfilled and completed the bounty) (`expired`, The bounty expired w/o completion) |

**Bounty Creator & Bounty Fulfiller**

|  Field Key                     | Datatype           |  Description                                             |
|--------------------------------|--------------------|----------------------------------------------------------|
| `bounty_owner_address`         | `ethereum_address` | Address of the person who owns the bounty                |
| `bounty_owner_email`           | `string`           | Email of the bounty owner                                |
| `bounty_owner_github_username` | `string`           | Username of the bounty owner                             |
| `metadata`                     | `dictionary`       | Misc metadata about the bounty and the creator           |
| `fulfiller_address`             | `ethereum_address` | Address of the person who fulfilled the bounty             |
| `fulfiller_email`                | `string`           | Email of the person fulfilling the bounty                  |
| `fulfiller_github_username`      | `string`           | Username of the fulfiller                                  |
| `fulfiller_metadata`             | `dictionary`       | `githubUsername` and `notificationEmail` for the fulfiller |

#### URL Parameters

**Filters**

You can filter the data returned from the API buy providing these keys as URL parameters `raw_data`, `experience_level`, `project_length`, `bounty_type`, `bounty_owner_address`, `is_open`, and `github_url`. `github_url` can take a comma-seperated list of GitHub urls

**Order By**

By passing an `order_by` parameter you can order the data by the provided key. Ex: `?order_by=expires_date`. To sort in the opposite direction you can add a `-` in from the the key `?order_by=-expires_date`.

#### Example Request

```
~ % curl "https://gitcoin.co/api/v0.1/bounties/?&order_by=web3_created"

[
  {
    "url": "https:\/\/gitcoin.co\/api\/v0.1\/bounties\/87\/",
    "created_on": "2017-09-22T01:42:07.060841Z",
    "modified_on": "2017-09-23T12:36:11.946334Z",
    "title": "Update local_settings.py.example",
    "web3_created": "2017-09-22T01:42:04Z",
    "value_in_token": "1000000000000000000.00",
    "token_name": "ETH",
    "token_address": "0x0000000000000000000000000000000000000000",
    "bounty_type": "",
    "project_length": "",
    "experience_level": "",
    "github_url": "https:\/\/github.com\/owocki\/pytrader\/pull\/83232",
    "bounty_owner_address": "0xd3d280c2866eaa795fc72bd850c48e7cce166e23",
    "bounty_owner_email": "ksowocki@gmail.com",
    "bounty_owner_github_username": "owocki",
    "fulfiller_address": "0x0000000000000000000000000000000000000000",
    "fulfiller_email": null,
    "fulfiller_github_username": null,
    "is_open": true,
    "expires_date": "2017-09-23T01:42:04Z",
    "raw_data": [
      1.0e+18,
      "0x0000000000000000000000000000000000000000",
      "0xd3d280c2866eaa795fc72bd850c48e7cce166e23",
      "0x0000000000000000000000000000000000000000",
      true,
      true,
      "https:\/\/github.com\/owocki\/pytrader\/pull\/83232",
      1506044524,
      "{\"issueTitle\":\"Update local_settings.py.example\",\"issueKeywords\":\"pytrader, owocki, Python, HTML, Shell\",\"tokenName\":\"ETH\",\"githubUsername\":\"owocki\",\"notificationEmail\":\"ksowocki@gmail.com\",\"experienceLevel\":\"\",\"projectLength\":\"\",\"bountyType\":\"\"}",
      1506130924,
      ""
    ],
    "metadata": {
      "githubUsername": "owocki",
      "experienceLevel": "",
      "projectLength": "",
      "tokenName": "ETH",
      "issueTitle": "Update local_settings.py.example",
      "bountyType": "",
      "issueKeywords": "pytrader, owocki, Python, HTML, Shell",
      "notificationEmail": "ksowocki@gmail.com"
    },
    "fulfiller_metadata": {

    },
    "current_bounty": true,
    "value_in_eth": 1.0e+18,
    "value_in_usdt": 280.65,
    "status": "expired",
    "now": "2017-09-24T18:59:53.964344Z"
  },
  ....
  ]

```

# WEB3 API

You may interact with the HTTPS API as follows

```
truffle(development)> BountyIndex.at('0x0ed0c2a859e9e576cdff840c51d29b6f8a405bdd').bountydetails.call('https://github.com/owocki/pytrader/pull/83');
[ { [String: '100000000000000000'] s: 1, e: 17, c: [ 1000 ] },
  '0x0000000000000000000000000000000000000000',
  '0xd3d280c2866eaa795fc72bd850c48e7cce166e23',
  '0x0000000000000000000000000000000000000000',
  true,
  true,
  'https://github.com/owocki/pytrader/pull/83',
  { [String: '1506220425'] s: 1, e: 9, c: [ 1506220425 ] },
  '{"issueTitle":"","issueKeywords":"","tokenName":"ETH","githubUsername":"owocki","notificationEmail":"ksowocki@gmail.com","experienceLevel":"","projectLength":"","bountyType":""}',
  { [String: '1537756425'] s: 1, e: 9, c: [ 1537756425 ] },
  '' ]

```

- be sure to replace `0x0ed0c2a859e9e576cdff840c51d29b6f8a405bdd` with the BountyIndex contract address.
- be sure to replace `https://github.com/owocki/pytrader/pull/83` with the issue that you care about.

Further information on the smart contract interface is available at [https://github.com/gitcoinco/smart_contracts/blob/master/contracts/bounty/BountyIndex.sol](https://github.com/gitcoinco/smart_contracts/blob/master/contracts/bounty/BountyIndex.sol)

_bountydetails function returns the following fields:

#### Fields

| Field Key          |  Datatype          | Description                                                       |
|--------------------|--------------------|-------------------------------------------------------------------|
| `amount`           | `float`            | Bounty amount in ETH or specified ERC20 token                     |
| `tokenAddress`     | `ethereum_address` | Address where the tokens are located                              |
| `bountyOwner`      | `ethereum_address` | Address of the person who owns the bounty                         |
| `claimee`          | `ethereum_address` | Address of the person who claimed the bounty                      |
| `open`             | `bool`             | True if the bounty has not been completed                         |
| `initialized`      | `bool`             | True if the bounty has been initialized                           |
| `issueURL`         | `string`           | URL on GitHub where you can find the bounty description           |
| `creationTime`     | `float`            | Creation timestamp                                                |
| `metaData`         | `string`           | Misc metadata about the bounty and the creator                    |
| `expirationTime`   | `float`            | Date before which the bounty must be completed                    |
| `fulfiller_metadata` | `string`           | githubUsername and notificationEmail for the claimee              |

# Running Locally

## With Docker

```shell
git clone https://github.com/gitcoinco/web.git
cd web
cp app/app/local_settings.py.dist app/app/local_settings.py
docker-compose up -d
```

Navigate to `http://0.0.0.0:8000/`.

*Note: Running `docker-compose logs --tail=50 -f <optional container_name>` will follow all container output in the active terminal window, while specifying a container name will follow that specific container's output. `--tail` is optional.*
Check out the [Docker Compose CLI Reference](https://docs.docker.com/compose/reference/) for more information.

## Without Docker

```shell
git clone https://github.com/gitcoinco/web.git
cd web/app
cp app/local_settings.py.dist app/local_settings.py
```

You will need to edit the `app/local_settings.py` file with your local settings. Look for config items that are marked `#required`.

## Setup Github OAuth2 App Integration

Navigate to: https://github.com/settings/applications/new and enter similar values to:

* Enter Application Name: `MyGitcoinApp`
* Homepage URL: `http://localhost`
* Application description: `My Gitcoin App`
* Authorization callback URL: `http://localhost:8000/` (required)

The authorization callback URL should match your `BASE_URL` value in `local_settings.py`

Set `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `GITHUB_APP_NAME` to the returned values.

## Setup Github User Integration

Navigate to:  https://github.com/settings/tokens/new
At minimum, select `user` scope.
Generate your token and copy it to:  `GITHUB_API_TOKEN`
Copy your Github username to:  `GITHUB_API_USER`

## Rollbar Integration

Error tracking is entirely optional and primarily for internal staging and production tracking.
If you would like to track errors of your local environment, setup an account at: https://rollbar.

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
```
psql
```
Create the database and a new privileged user.
```sql
CREATE DATABASE gitcoin;
CREATE USER gitcoin_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gitcoin TO gitcoin_user;
```
Exit Postgres session
```
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


```
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

```
./manage.py sync_geth mainnet 0 99999999999
```

# Adding your token to Gitcoin.

Have an ERC20 compatible token that you'ud like to add support for?  Great!

[Here is an example of how to do it](https://github.com/gitcoinco/web/pull/155)

# Legal

'''
    Copyright (C) 2017 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

# License
[GNU AFFERO GENERAL PUBLIC LICENSE](./docs/LICENSE)

<!-- Google Analytics -->
<img src='https://ga-beacon.appspot.com/UA-102304388-1/gitcoinco/web' style='width:1px; height:1px;' >
