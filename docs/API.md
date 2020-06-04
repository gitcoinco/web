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

The bounties endpoint provides a listing of bounties and their current status. There is one endpoint that access bounties:

- `https://gitcoin.co/api/v0.1/bounties/` - Returns a list of bounties

#### Fields

| Field Key          |  Datatype          | Description                                                       |
|--------------------|--------------------|-------------------------------------------------------------------|
| `url`              | `string`           | URL for this specific bounty Ex: api/v0.1/bounties/9/              |
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
| `github_org_name`       | `string`           | github org name         |
| `github_repo_name`       | `string`           | github repo name           |
| `github_issue_number`       | `string`           | github issue number           |
| `keywords`       | `string`           | comma delimited list of keywords           |
| `current_bounty`   | `boolean`          | Whether this bounty is the most current revision one or not       |
| `expires_date`     | `date_time`        | Date before which the bounty must be compelted                    |
| `value_in_eth`     | `integer`          | Value of the bounty in Ethereum                                   |
| `value_in_usdt`    | `float`            | Approximation of value in USD at bounty web3_created timestamp    |
| `value_in_usdt_now`| `float`            | Approximation of current value in USD                             |
| `now`              | `date_time`        | Current date_time on the server                                   |
| `action_urls`              | `dict`        | a list of urls where user can take action against the bounty                                   |
| `paid`              | `array`        | List of users who have been paid from the bounty                             |

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

You can filter the data returned from the API by providing these keys as URL parameters `experience_level`, `project_length`, `bounty_type`, `bounty_owner_address`, `is_open`, `github_url` and `pk`. `github_url` can take a comma-separated list of GitHub urls. `pk` takes an ID and returns a single bounty.


**Order By**

By passing an `order_by` parameter you can order the data by the provided key. Ex: `?order_by=expires_date`. To sort in the opposite direction you can add a `-` in from the the key `?order_by=-expires_date`.

#### Example Request

```shell
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
    "fulfiller_metadata": {

    },
    "current_bounty": true,
    "value_in_eth": 1.0e+18,
    "value_in_usdt_now": 280.65,
    "status": "expired",
    "now": "2017-09-24T18:59:53.964344Z"
  },
  ....
  ]

```

### `grants`

The grants endpoint provides a listing of grants and all it's information. There is one endpoint that access grants:

- `https://gitcoin.co/api/v0.1/grants/` - Returns a list of grants

#### Fields

| Field Key          |  Datatype          | Description                                                       |
|--------------------|--------------------|-------------------------------------------------------------------|
| `active`           | `boolean`          | Whether or not the Grant is active                                |
| `title`            | `string`           | Title of the Grant                                                |
| `slug`             | `string`           | Slug for the Grant populated from `title`                         |
| `description`      | `string`           | Description of the Grant                                          |
| `reference_url`    | `string`           | Associated reference URL of the Grant                             |
| `logo`             | `string`           | URL of the Grant logo image                                       |
| `admin_address`    | `ethereum_address` | Wallet address of the Grant Admin where subscription funds will be sent |
| `amount_received`  | `float`            | Total amount of contributions received by the Grant in USDT/DAI   |
| `token_address`    | `ethereum_address` | Address of the token to be used with the Grant                    |
| `token_symbol`     | `token_type`       | Type of token to be used with the Grant                           |
| `contract_address` | `ethereum_address` | Contract address of the Grant                                     |
| `metadata`         | `dictionary`       | Misc metadata about the Grant                                     |
| `network`          | `string`           | Network in which the Grant contract resides                       |
| `required_gas_price`| `float`           | Required gas price for the Grant                                  |
| `admin_profile`    | `dictionary`       | Grant Admin's profile                                             |
| `team_members`     | `array`            | Array of Dictionaries of team members contributing to this Grant  |

**Profile**:

|  Field Key         | Datatype           |  Description                                             |
|--------------------|--------------------|----------------------------------------------------------|
| `id`               | `integer`          | Profile ID                                               |
| `url`              | `string`           | URL to the Gitcoin profile                               |
| `handle`           | `string`           | GitHub handle/username associated with the Profile       |
| `keywords`         | `array`            | Array of keywords associated with the Profile            |
| `position`         | `integer`          | Position of the Profile in the `Weekly Earners` leaderboard |
| `avatar_url`       | `string`           | URL to the Gitcoin Avatar of the Profile                 |
| `github_url`       | `string`           | URL to the GitHub profile                                |
| `total_earned`     | `float`            | Sum of  ETH collected by the profile                     |
| `organizations`    | `dictionary`       | Dictionary containing profiles that this user works with |


#### URL Parameters

**Filters**

You can filter the data returned from the API by providing these keys as URL parameters `title`, `description`, `keyword`, `grant_type` and `pk` that takes an ID and returns a single grant.


#### Example Request

```shell
~ % curl "https://gitcoin.co/api/v0.1/grants/?grant_type=tech"

[
  {
    "active": true,
    "title": "Cipher Dogs Team",
    "slug": "cipher-dogs-team",
    "description": "Our team is interested in electronic art/hack/social activity and blockchain/decentralized technology and other technologies. We are aimed at promoting blockchain technology among people. Our team creates various libraries, websites, artwork and other projects in the field of blockchain technologies. We also help blockchain projects. We believe that blockchain technology is the future.\r\n",
    "reference_url": "https://github.com/CipherDogs",
    "logo": "https://c.gitcoin.co/grants/1a573aca695eada7c2f9badf1ed84b10/cipher1.png",
    "admin_address": "0xD12Dd8aEb8F96D0bFF6aA9C74bDf92009741d3Aa",
    "amount_received": "0.0000",
    "token_address": "0x0000000000000000000000000000000000000000",
    "token_symbol": "Any Token",
    "contract_address": "0xbcAE3e2893722698535aaf355F0aA92CA846354F",
    "metadata": {},
    "network": "mainnet",
    "required_gas_price": "0",
    "admin_profile": {
      "id": 82330,
      "url": "/deadblackclover",
      "handle": "deadblackclover",
      "keywords": [
        "Rust",
        "Scala",
        "JavaScript",
        "HTML",
        "CSS",
        "Emacs Lisp",
        "C#",
        "Vue",
        "Shell"
      ],
      "position": 0,
      "avatar_url": "https://c.gitcoin.co/avatars/0aee35065024a0382c19e5a30fb2349c/deadblackclover.png",
      "github_url": "https://github.com/deadblackclover",
      "total_earned": 0,
      "organizations": {}
    },
    "team_members": [
      {
        "id": 82330,
        "url": "/deadblackclover",
        "handle": "deadblackclover",
        "keywords": [
          "Rust",
          "Scala",
          "JavaScript",
          "HTML",
          "CSS",
          "Emacs Lisp",
          "C#",
          "Vue",
          "Shell"
        ],
        "position": 0,
        "avatar_url": "https://c.gitcoin.co/avatars/0aee35065024a0382c19e5a30fb2349c/deadblackclover.png",
        "github_url": "https://github.com/deadblackclover",
        "total_earned": 0,
        "organizations": {}
      }
    ]
  },
  ...
]
```

# WEB3 API

You may interact with the HTTPS API as follows

```shell
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
| `amount_denomination`     | `string` | Denomination of the bounty                              |
| `action_url`         | `string`           | URL of the bounty           |
| `title`         | `string`           | Title of hte bounty           |
| `description`         | `string`           | Description of the bounty           |
| `created_on`     | `datetime`            | Creation timestamp                                                |
| `source_project`         | `string`           | Source Project the bounty came from           |
| `tags`         | `strings`           | tags to classify the bounthy           |
