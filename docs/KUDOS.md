
## You guys just launched [Kudos](https://gitcoin.co/kudos).  How do I get/test kudos on my local RPC node?

This answer assumes you're using docker. 

Run these commands

```
# start from the directory on your local filesystem that contains the gitcoinco web repo
cd ..
git clone git@github.com:gitcoinco/Kudos721Contract.git
cd Kudos721Contract
npm install openzeppelin
cd ../web
bash scripts/mint_test_kudos.bash

```

The above commands clone the Kudos smart contract, installs the dependancies, deploys the smart contract to ganache, and mints several kudos in the newly minted smart contract.

After the `scripts/mint_test_kudos.bash` script runs, you will have kudos on your local docker container, via the localhost RPC node


## Where is Kudos deployed?

Please checkout [the github repo for Kudos](https://github.com/gitcoinco/Kudos721Contract) to see this information.

## Can I see the Kudos security audit?

Please checkout [the github repo for Kudos](https://github.com/gitcoinco/Kudos721Contract) to see this information.

## What is Kudos Direct Send?

Kudos Direct Send (KDS) is a direct send of a Kudos ERC 721 NFT from one Ethereum address to another.

## What is Kudos Indirect Send?

Kudos Indirect Send (KIS) enables Gitcoin users to send a Kudos to *any github/gitcoin username*.  KIS is effectively a proxy account that can hold a Kudos 721 NFT until a recipient (who is authorized by a github username) claims it.  

The Kudos Indirect send architecture diagram is available [here](https://github.com/gitcoinco/web#of-a-tip)

## When is Kudos Indirect Send used and when is Kudos Direct Send Used?

If a user has set a preferred Ethereum address in their [account](https://gitcoin.co/settings/account), KDS will be used.  

If not, KIS will be used.



