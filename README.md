<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/263e3q1M2Y2r3L1X3c2y/helmet.png'/>

# Gitcoin

Gitcoin pushes Open Source Forward.  Learn more at [https://gitcoin.co](https://gitcoin.co)

# web repo

This is the website that is live at gitcoin.co

## What

Functionally, the app has several key features:

* Smart Contracts -- Where bounties are stored and indexed.
* Brochureware -- Describes the project
* Bounty Explorer -- A searchable index of all of the work available in the system.
* Bounty Submission / Acceptance flow -- Interface between the application and web3.

Technically, the system is architected:

* __Web3__ The main source of truth for the system is the Ethereum blockchain.  Check out the [smart contracts](https://github.com/gitcoinco/smart_contracts).
* __Web2__ This part of the app is built with Python, Django, Postgres, and a handful of other tools that are common in the web2 ecosystem.
* __Web 3 Bridge__ This is the bridge between web3 and the rest of the application.  Mostly built in javascript(web3js) and python(web3py).
* __Brochureware__ Just a nice little landing page telling folks what the Gitcoin project is.

# HTTPS API

You may interact with the HTTPS API as follows

```
~ % curl "http://gitcoin.co/api/v0.1/bounties/?&order_by=web3_created"

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
    "claimeee_address": "0x0000000000000000000000000000000000000000",
    "claimee_email": null,
    "claimee_github_username": null,
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
    "claimee_metadata": {
      
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

[There is a bounty on adding more documentation to the API.](https://github.com/gitcoinco/web/issues/1).  Please feel free to take a stab at it.


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


# Adding your token to Gitcoin.

Have an ERC20 compatible token that you'ud like to add support for?  Great!

1. Edit `web/app/assets/js/tokens.js` and add your token.
1. Edit `web/app/dashboard/tokens.py` and add your token.
1. Submit a PR against this repo.

# Legal

'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''



<!-- Google Analytics -->
<img src='https://ga-beacon.appspot.com/UA-102304388-1/gitcoinco/web' style='width:1px; height:1px;' >

