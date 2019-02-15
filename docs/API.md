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

- `https://gitcoin.co/api/v0.1/bounties/` - Returns a list of bounties
- `https://gitcoin.co/api/v0.1/bounties/<bountyId>/` - Returns a single bounty by ID.

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

You can filter the data returned from the API by providing these keys as URL parameters `experience_level`, `project_length`, `bounty_type`, `bounty_owner_address`, `is_open`, and `github_url`. `github_url` can take a comma-seperated list of GitHub urls

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
| `amount_denomination`     | `string` | Denomination of the bounty                              |
| `action_url`         | `string`           | URL of the bounty           |
| `title`         | `string`           | Title of hte bounty           |
| `description`         | `string`           | Description of the bounty           |
| `created_on`     | `datetime`            | Creation timestamp                                                |
| `source_project`         | `string`           | Source Project the bounty came from           |
| `tags`         | `strings`           | tags to classify the bounthy           |
