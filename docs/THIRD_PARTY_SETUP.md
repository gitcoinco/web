# Third party integrations

## Setup Github OAuth2 App Integration (Recommended)

Navigate to: [Github - New Application](https://github.com/settings/applications/new) and enter similar values to:

* Enter Application Name: `MyGitcoinApp`
* Homepage URL: `http://localhost`
* Application description: `My Gitcoin App`
* Authorization callback URL: `http://localhost:8000/` (required)

The authorization callback URL should match your `BASE_URL` value in `web/app/app/.env`

Update the `web/app/app/.env` file to include the values provided by Github:

```shell
GITHUB_CLIENT_ID=xxxx
GITHUB_CLIENT_SECRET=xxx
GITHUB_APP_NAME=MyGitcoinApp
```

Please `docker-compose down; docker-compose up -d` to have the environment variable changes reflect in your local Gitcoin environment.

## Setup Github User Integration (Recommended)

Navigate to: [Github - New Token](https://github.com/settings/tokens/new)
At minimum, select `user` scope.

Update the `web/app/app/.env` file to include the values provided by Github:

```shell
GITHUB_API_TOKEN=xxx
GITHUB_API_USER=xxx
```

Make sure you disable gitcoinbot notifications on your local, unless you are specifically testing that feature
By default, we disable outbound GitHub notifications to any repository that isn't under the `GITHUB_API_USER` repositories.

For example, if `settings.GITHUB_API_USER == gitcoinco` only `github.com/gitcoinco/<repos>` bounties and associated tips will post Github comments.

## Setup Google Verification Integration

Navigate to: [Google - New Project](https://console.developers.google.com/) and enter similar values to:

* Enter Project Name: `MyGitcoinApp`

Navigate to: [Google - OAuth consent screen](https://console.developers.google.com/apis/credentials/consent?) and create an `external` OAuth consent screen:

* Application name: `MyGitcoinApp`
* Support email: Select your email

Navigate to: [Google - Credentials](https://console.developers.google.com/apis/credentials) and create OAth Client ID:

* Application Type: `Web Application`
* Name: `MyGitcoinApp`
* Authorized JavaScript origins: `http://localhost:8000`
* Authorized redirect URIs: `http://localhost:8000/api/v0.1/profile/verify_user_google`

Update the `web/app/app/.env` file to include the values provided by Google:

```shell
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
```

Please `docker-compose down; docker-compose up -d` to have the environment variable changes reflect in your local Google environment.

Note: Update the `OAUTHLIB_INSECURE_TRANSPORT` in `web/app/app/.env` to `0` for production.

## Setup Facebook Integration

Navigate to: [Facebook - Create App](https://developers.facebook.com/apps/), select `Build Connected Experiences` and continue with similar values to:
* App Display Name: `MyGitcoinApp`
* App Contact Email: Your email address

Set Up Facebook Login in **Add Products to Your App**.

On the page: `Facebook Login > Settings`:
* Valid OAuth Redirect URIs: `http://localhost:8000`

Update the `web/app/app/.env` file to include the values provided by Facebook on your created app `Settings > Basic`:

```sell
FACEBOOK_CLIENT_ID=xxx
FACEBOOK_CLIENT_SECRET=xxx
```

Please `docker-compose down; docker-compose up -d` to have the environment variable changes reflect in your local Gitcoin environment.

## Setup SendGrid to Send Emails (Recommended)

1. Create a new SendGrid Account at https://sendgrid.com
2. Go to [https://app.sendgrid.com/settings/api_keys](https://app.sendgrid.com/settings/api_keys) and create a new Sendgrid API key:

Update the `web/app/app/.env` file to include the values provided by SendGrid:

```shell
SENDGRID_API_KEY=xxx
CONTACT_EMAIL=xxx
```

```shell
# Be VERY CAREFUL when changing this setting.  You don't want to accidently
# send a bunch of github notifications :)
ENABLE_NOTIFICATIONS_ON_NETWORK=None
```

## Setup Fortmatic Integration

1. Sign up/Login to Fortmatic dashboard at https://dashboard.fortmatic.com
2. Update the `web/app/app/.env` file to include the values provided by Fortmatic:

```shell
FORTMATIC_LIVE_KEY=xxx
FORTMATIC_TEST_KEY=xxx
```

## Gitcoinbot Installation Instructions

### This integration requires the Github OAuth2 App Integration

Navigate to: [Gitcoinbot Github App](https://github.com/apps/gitcoinbot)
Copy the application ID found on the page as the `GITCOINBOT_APP_ID` environment variable.

Make sure you disable gitcoinbot notifications on your local, unless you are specifically testing that feature

```shell
# Be VERY CAREFUL when changing this setting.  You don't want to accidentally
# send a bunch of github notifications :)
ENABLE_NOTIFICATIONS_ON_NETWORK=None
```

The following environment variables must be set for gitcoinbot to work correctly:

```shell
GITHUB_API_USER=gitcoinbot  # Github Profile name of the bot. Defaults to: gitcoinbot
GITCOINBOT_APP_ID=APP_ID_FROM_ABOVE  # Defaults to empty.
GITCOIN_BOT_CERT_PATH=RELATIVE_PATH_TO_CERT_FILE  # Defaults to empty.
```

#### Example

```shell
GITHUB_API_USER=gitcoinbot  # Github Profile name of the bot. Defaults to: gitcoinbot
GITCOINBOT_APP_ID=7735  # Gitcoin Bot App ID
GITCOIN_BOT_CERT_PATH=app/gitcoin_bot_secret.pem  # If pem file is located at web/app/app/gitcoin_bot_secret.pem
```

Aside from these environment variables, the settings page of the gitcoin bot application must have the correct url for webhook events to post to. It should be set to `https://gitcoin.co/payload` based on urls.py line 131.

After running the migrations and deploying the gitcoin.co website, gitcoinbot will begin to receive webhook events from any repository that it is installed into. This application will then parse through the comments and respond if it is called with @gitcoinbot + registered action call.

## Sentry Integration

Error tracking is entirely optional and primarily for internal staging and production tracking.
If you would like to track errors of your local environment, setup an account at: [Sentry.io](https://sentry.io)

Once you have access to your project secrets, you can enable Sentry error tracking for both the backend and frontend by adding the following environment variables to `web/app/app/.env`:

```shell
SENTRY_DSN=xxx
```

## [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) with DIDKit

You can use [DIDKit](https://github.com/spruceid/didkit) to generate a private
key to sign the verifiable credentials.

It can be installed with `cargo`, the package manager for [Rust](https://www.rust-lang.org/),
easily obtained with the [`rustup`](https://rustup.rs/) installer.

```shell
$ cargo install didkit-cli
```

The subcommand `generate-ed25519-key` will output a Ed25519 key in JWK format
that you can then add to your `.env`.

```shell
$ didkit generate-ed25519-key
{"kty":"OKP","crv":"Ed25519","x":"xyzw","d":"abcd"}

DIDKIT_JWK_KEY={"kty":"OKP","crv":"Ed25519","x":"xyzw","d":"abcd"}
```

As the issuer, you will have to decide on a [DID](https://www.w3.org/TR/did-core/)
method to use to create your DID and identify the signer.

One of them is [`did-web`](https://w3c-ccg.github.io/did-method-web/) which works
by hosting your DID document, a file called `did.json`, under the specified domain
and path. For example, the DID `did:web:domain.tld:subpath` would look for the
file under `domain.tld/subpath/.well-known/did.json`, and `did:web:domain.tld`
would look at `domain.tld/.well-known/did.json`.

```shell
POPP_VC_ISSUER=did:web:domain.tld
```

If you opt to use a `did-web` DID, the `did.json` file should include the public
information of the key used to sign the credentials like in the example that
follows.

```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:web:domain.tld",
  "verificationMethod": [{
    "id": "did:web:domain.tld#default",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:web:domain.tld",
    "publicKeyJwk": {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "xyzw"
    }
  }],
  "authentication": ["did:web:domain.tld#default"],
  "assertionMethod": ["did:web:domain.tld#default"]
}
```

The last environment variable to be used with the VC integrations is `POPP_VC_VERIFIER`
which is simply what the `Verify` button will link to when the user clicks on it.
It should point to a tool that helps the user verify and/or understand the VC
that was issued to them.

```shell
POPP_VC_VERIFIER=https://example.tld/popp-tools
```
