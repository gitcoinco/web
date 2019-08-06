<img src="https://d3vv6lp55qjaqc.cloudfront.net/items/263e3q1M2Y2r3L1X3c2y/helmet.png" width=75px height=75px>

# Gitcoin

Gitcoin Grows Open Source. Learn more at [https://gitcoin.co](https://gitcoin.co)

<a href="https://gitcoin.co/explorer?q=gitcoinco">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/gitcoinco/web&badge=1&maxAge=60">
</a>

# web repo

[![Build Status](https://travis-ci.org/gitcoinco/web.svg?branch=master)](https://travis-ci.org/gitcoinco/web)
[![codecov](https://codecov.io/gh/gitcoinco/web/branch/master/graph/badge.svg)](https://codecov.io/gh/gitcoinco/web)

This is the website that is live at [gitcoin.co](https://gitcoin.co)
```master``` branch - staging
```stable``` branch - live on gitcoin.co

## Documentation

[https://docs.gitcoin.co](https://docs.gitcoin.co)

## How to interact with this repo

### Table of Contents

- [Gitcoin](#gitcoin)
- [web repo](#web-repo)
  * [How to interact with this repo](#how-to-interact-with-this-repo)
    + [On Github](#on-github)
    + [On Gitcoin](#on-gitcoin)
  * [What](#what)
- [Developing](#developing)
  * [HTTPS API](#https-api)
  * [Running Locally](#running-locally)
- [Trying out Gitcoin](#trying-out-gitcoin)
  * [Posting your first issue](#posting-your-first-issue)
- [Integrating Gitcoin](#integrating-gitcoin)
  * [Integrating the 'available work widget' on your repo.](#integrating-the--available-work-widget--on-your-repo)
  * [Adding GitcoinBot to your repo](#adding-gitcoinbot-to-your-repo)
  * [Adding your token to Gitcoin](#adding-your-token-to-gitcoin)
- [Legal](#legal)
- [License](#license)

### On Github

[Star](https://github.com/gitcoinco/web/stargazers) and [watch](https://github.com/gitcoinco/web/watchers) this github repository to stay up to date, we're pushing new code several times per week!

Check out the [CHANGELOG](https://docs.gitcoin.co/mk_changelog/) for details about recent changes to this repository.

Also,

* want to become a contributor ? Checkout our [guidelines](https://docs.gitcoin.co/mk_contributors/) & [styleguide](https://docs.gitcoin.co/mk_styleguide/).
* [check out the gitcoinco organization-wide repo](https://github.com/gitcoinco/gitcoinco).
* check out the open issues list, especially the [discussion](https://github.com/gitcoinco/web/issues?q=is%3Aissue+is%3Aopen+label%3Adiscussion) label and [easy-pickings](https://github.com/gitcoinco/web/issues?q=is%3Aissue+is%3Aopen+label%3Aeasy-pickings).

### On Gitcoin

[Check out the available open issues on Gitcoin](https://gitcoin.co/explorer/?q=https://github.com/gitcoinco/web).

## What is Gitcoin?

Functionally, the app has several key features:

* Smart Contracts -- Where funded issues are stored and indexed.
* Brochureware -- Describes the project.
* Funded Issue Explorer -- A searchable index of all of the work available in the system.
* Funded Issue Submission / Acceptance flow -- Interface between the application and web3.
* API - the HTTPS API
* Bot - the GitcoinBot

[More about how/why to interact with web3 here](https://gitcoin.co/web3).

Technically, the system is architected:

* __Web3__ The main source of truth for the system is the Ethereum blockchain. Check out the [smart contracts](https://github.com/gitcoinco/smart_contracts).
* __Web2__ This part of the app is built with Python, Django, Postgres, and a handful of other tools that are common in the web2 ecosystem.
* __Web 3 Bridge__ This is the bridge between web3 and the rest of the application. Mostly built in javascript(web3js) and python(web3py).
* __Brochureware__ Just a nice little landing page telling folks what the Gitcoin project is.

# Developing

## HTTPS API

[For more information on the HTTPS API, please view the api README](https://docs.gitcoin.co/mk_rest_api/)

## Running locally

### With Docker (Recommended)

[For more information on running the app locally, please view the documentation for running gitcoinco/web with Docker](https://docs.gitcoin.co/mk_setup/)

### Without Docker

[For more information on running the app locally, please view the documentation for running gitcoinco/web without Docker](https://docs.gitcoin.co/mk_alternative_setup/)

## Overriding Application Defaults

[For more information on overriding the local dev environment configuration defaults, please view the environment variables documentation](https://docs.gitcoin.co/mk_envvars/)

# Trying out Gitcoin

## Posting your first issue

If you

* have some work on your Github Issues board that you don't have time (or skills) to do.
* are dependant upon an upstream repo for something, and you'd like to incentivize them to work onit.

try posting a funded issue at [https://gitcoin.co/new](https://gitcoin.co/new).

# Integrating Gitcoin

Basics

* [Getting Started With Gitcoin](https://medium.com/gitcoin/getting-started-with-gitcoin-fa7149f2461a)
* [Fund an Issue on Gitcoin](https://medium.com/gitcoin/fund-an-issue-on-gitcoin-3d7245e9b3f3)

Advanced

* [Make a Contributor Friendly Repo](https://medium.com/gitcoin/how-to-build-a-contributor-friendly-project-927037f528d9)
* [Set your OSS repos monetary policy](https://medium.com/gitcoin/setting-your-oss-repos-monetary-policy-9c493118cd34)
* [Payout Several Contribs at Once](https://medium.com/gitcoin/payout-several-contributors-at-once-8742c13a8fdd)
* [Crowdfund Bounties](https://medium.com/gitcoin/crowdfunding-bounties-fd821b04309d)
* [Make a Gitcoin ENS Name](https://medium.com/gitcoin/personalize-your-own-gitcoin-ens-name-f8e5d7438e3e)

Background

* [Everything you need to know about Gitcoin](https://medium.com/gitcoin/everything-you-need-to-know-about-gitcoin-fe2e3e292a21)
* [Our Vision: Open Source Money will BUIDL the OSS Ecosystem](https://medium.com/gitcoin/open-source-money-will-buidl-the-open-source-ecosystem-f4169def8748)

Testimonials & Case Studies

* [Augur](https://medium.com/gitcoin/gitcoin-testimonials-augur-9bfe97368a30)
* [Balance](https://medium.com/gitcoin/gitcoin-testimonials-balance-6d027fe01b9f)
* [uPort](https://medium.com/gitcoin/gitcoin-testimonials-uport-1510222f3744)
* [Ethereum Foundation](https://medium.com/gitcoin/gitcoin-testimonials-ethereum-foundation-web3py-py-evm-561cd4da92a6)
* [Market Protocol](https://medium.com/gitcoin/gitcoin-testimonials-market-protocol-722dbb263d19)

## Integrating the 'available work widget' into your repository

This widget will help you advertise that you support Gitcoin bounties, so that your community knows the best place to contribute.

[Check out the widget documentation to learn how](https://docs.gitcoin.co/mk_widget/)

## Adding GitcoinBot to your repo

Gitcoinbot will allow you to add issues straight from github.

[Check out the gitcoinbot readme to learn how](../app/gitcoinbot/README.md)

## Adding your token to Gitcoin

Have an ERC20 compatible token that you'd like to use on the platform?  Great!  Submit [this form](https://gitcoin.co/submittoken) to submit it to the system

## High Level flows...

### ... of a Bounty

This is the high level flow of a bounty on Gitcoin:

<a href="https://www.draw.io/?state=%7B%22ids%22:%5B%221FTatOur159qS8pzBCgIG5E0XdEH8iZF-%22%5D,%22action%22:%22open%22,%22userId%22:%22115514289174042120922%22%7D#G1FTatOur159qS8pzBCgIG5E0XdEH8iZF-"><img src='https://github.com/gitcoinco/web/raw/master/docs/bounty_flow.png'></a>

Chain of Custody

1. Bounty Funder's Wallet
2. [StandardBounties Smart Contract](https://github.com/Bounties-Network/StandardBounties) deployed at [0x2af47a65da8cd66729b4209c22017d6a5c2d2400](https://etherscan.io/address/0x2af47a65da8cd66729b4209c22017d6a5c2d2400#code)
3. (Submission Made)
4. (Submission Accepted)
5. Recipient's Wallet

Anywhere between 2 and 4 above, Funder may withdraw their funds via 'Cancel Bounty' function for any reason.

We may introduce Arbitration [via Delphi](http://delphi.network/) at some point in the future.  Until then, we are lucky that Github users are very protective of their reputation, and therefore very kind to each other, and disputes have not generally arisen.

### of a Tip

### ... of a Kudos

Note:
- Crowdfunded bounties + bulk payouts are secured by Tips (at least until Standard Bounties 2.0 is released).
- Kudos are also secured by Tips

This is the high level flow of a tip on Gitcoin:

<a href="https://www.draw.io/#G1sTJtQou5FYsHCabhb2JXHDTprpvvkUy0"><img src='https://github.com/gitcoinco/web/raw/master/docs/tip_flow.png'></a>

# Licenses

- [Code - GNU AFFERO GENERAL PUBLIC LICENSE](../LICENSE)
- [Creative assets -- Attribution-NonCommercial-NoDerivatives 4.0 International](../app/assets/LICENSE.txt)

<!-- Google Analytics -->
<img src='https://ga-beacon.appspot.com/UA-102304388-1/gitcoinco/web' style='width:1px; height:1px;' >
