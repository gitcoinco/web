# Recognoized Environment Variables

The following environment variables are currently accepted by the local web application.
You can overwrite the default values for these environment variables by adding them to the `web/app/app/.env` file.
All of the environment variables used by this application conform to the [`django-environ` documentation](https://django-environ.readthedocs.io/en/latest/).

## Initial Overrides

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| CACHE_URL | The [`django-environ`](https://django-environ.readthedocs.io/en/latest/#supported-types) compatible uri to your cache. | `str` | dbcache://my_cache_table |
| DATABASE_URL | The [`django-environ`](https://django-environ.readthedocs.io/en/latest/#supported-types) compatible uri to your database. | `str` | psql://postgres:postgres@db:5432/postgres |
| DEBUG | Whether or not to run the environment in Debug mode. | `bool` | True |
| SECRET_KEY | The secret key to use for your Django environment. | `str` | TODO |

## Amazon Web Services

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| AWS_ACCESS_KEY_ID | Your AWS access key ID. | `str` | '' |
| AWS_SECRET_ACCESS_KEY | Your AWS secret access key | `str` | '' |
| S3_REPORT_BUCKET | The S3 bucket to be used to store reports. | `str` | TODO |
| S3_REPORT_PREFIX | The S3 path prefix to be used when storing reports. | `str` | TODO |

## Colorado Coin

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| COLO_ACCOUNT_ADDRESS | The coin distribution address. | `str` | '' |
| COLO_ACCOUNT_PRIVATE_KEY | The coin distribution private key. | `str` | '' |

## EthOS

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| ETHOS_CONTRACT_ADDRESS | The coin contract address. | `str` | '' |
| ETHOS_ACCOUNT_ADDRESS | The coin distribution address. | `str` | '' |
| ETHOS_ACCOUNT_PRIVATE_KEY | The coin distribution private key. | `str` | '' |
| ETHOS_TWITTER_CONSUMER_KEY | EthOSEthereal Twitter account consumer key. | `str` | '' |
| ETHOS_TWITTER_CONSUMER_SECRET | EthOSEthereal Twitter account consumer secret. | `str` | '' |
| ETHOS_TWITTER_ACCESS_TOKEN | EthOSEthereal Twitter account access token. | `str` | '' |
| ETHOS_TWITTER_ACCESS_SECRET | TEthOSEthereal Twitter account access secret. | `str` | '' |

## Django

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| INSTALLED_APPS | A list of additional apps to be recognized by Django. | `list` | [] |

## Github Authentication

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| GITHUB_API_BASE_URL | The Github API URL. | `str` | https://api.github.com |
| GITHUB_AUTH_BASE_URL | The Github OAuth authorization URL. | `str` | https://github.com/login/oauth/authorize |
| GITHUB_TOKEN_URL | The Github OAuth access token URL. | `str` | https://github.com/login/oauth/access_token |
| GITHUB_SCOPE | The Github application scope. | `str` | read:user,user:email,read:org |
| GITHUB_CLIENT_ID | The client ID of the Github OAuth app. | `str` | TODO |
| GITHUB_CLIENT_SECRET | The client secret of the Github OAuth app. | `str` | TODO |
| GITHUB_API_USER | The username of the Github account. | `str` |TODO |
| GITHUB_API_TOKEN | The token of the Github account. | `str` | TODO |
| GITHUB_APP_NAME | The name of your Github OAuth application. | `str` | gitcoin-local |


## Gitcoin Bot

For further information, please check out the [Gitcoin Bot Documentation](https://github.com/gitcoinco/web/blob/master/app/gitcoinbot/README.md).

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| GITCOINBOT_APP_ID | The Gitcoin Bot App ID provided by Github. | `str` | '' |
| GITCOIN_BOT_CERT_PATH | The relative path to the Gitcoin Bot pem certificate. | `str` | '' |
| GITHUB_EVENT_HOOK_URL | The Github event hook payload URL for Gitcoin Bot. | `str` | github/payload/ |
| IGNORE_COMMENTS_FROM | A list of Github handles to ignore comments from. | `list` | ['gitcoinbot', ] |

## Rollbar

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| ROLLBAR_SERVER_TOKEN | The [Rollbar](https://rollbar.com) server token from your Rollbar account settings. | `str` | '' |
| ROLLBAR_CLIENT_TOKEN | The [Rollbar](https://rollbar.com) client token from your Rollbar account settings. | `str` | '' |

## SendGrid

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| SENDGRID_EVENT_HOOK_URL | The SendGrid event hook URL. | `str` | sg_event_process |

## Slack

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| SLACK_TOKEN | The API token to be used for interacting with Slack. | `str` | TODO |

## Silk

The below environment variables are useful for overwriting [Django Silk](https://github.com/jazzband/django-silk) settings.

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| ENABLE_SILK | Whether or not to enable the [Django Silk](https://github.com/jazzband/django-silk) profiling and inspection tool. | `bool` | False |
| SILKY_PYTHON_PROFILER | Whether or not to enable the [function profiler](https://github.com/jazzband/django-silk#profiling). | `bool` | True |
| SILKY_PYTHON_PROFILER_BINARY | Whether or not to enable the generation of `.prof` files. | `bool` | False |
| SILKY_AUTHENTICATION | Whether or not to require [user authentication](https://github.com/jazzband/django-silk#authenticationauthorisation) to access Silk. | `bool` | False |
| SILKY_AUTHORISATION | Whether or not to require `is_staff` to access Silk. | `bool` | False |
| SILKY_META | Whether or not to enable [meta profiling](https://github.com/jazzband/django-silk#meta-profiling). | `bool` | True |
| SILKY_INTERCEPT_PERCENT | Limit the number of [request/responses](https://github.com/jazzband/django-silk#recording-a-fraction-of-requests) stored by Silk. | `int` | 100 |
| SILKY_MAX_RECORDED_REQUESTS | Limit the number of request/response rows stored by Silk. | `int` | 10000 |
| SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT | The percent of recorded data to perform gargbase collection on.  | `int` | 10 |
| SILKY_DYNAMIC_PROFILING |  | `dict` | {} |

## Web3

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| WEB3_HTTP_PROVIDER | The Web3 HTTP provider URI to be used. | `str` | https://rinkeby.infura.io |


## Miscellaneous

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| FAUCET_AMOUNT | The amount of ETH to be distributed for approved faucet requests. | `float` | .0005 |
| GITTER_TOKEN | The Gitter chat API token. | `str` | False |
