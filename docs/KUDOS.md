# Kudos General Documentation

## How to populate my DB with kudos

First be aware to update your `.env` with this entries

```
KUDOS_NETWORK=rinkeby
KUDOS_OWNER_ACCOUNT= YOUR_ADDRESS
KUDOS_LOCAL_SYNC=off
```
Then run the commands

```shell
docker-compose up
docker-compose exec web bash -c 'cd app && python manage.py sync_kudos rinkeby filter --start earliest'
```

## How do I MINT kudos on my local RPC node

This answer assumes you're using docker.

Run these commands

```shell
# start from the directory on your local filesystem that contains the gitcoinco web repo
cd ..
git clone git@github.com:gitcoinco/Kudos721Contract.git
cd Kudos721Contract
npm install openzeppelin
cd ../web
bash scripts/mint_test_kudos.bash
```

The above commands clone the Kudos smart contract, installs the dependencies, deploys the smart contract to ganache, and mints several kudos in the newly minted smart contract.

After the `scripts/mint_test_kudos.bash` script runs, you will have kudos on your local docker container, via the localhost RPC node

## Where is Kudos deployed

Please checkout [the github repo for Kudos](https://github.com/gitcoinco/Kudos721Contract) to see this information.

## Can I see the Kudos security audit

Please checkout [the github repo for Kudos](https://github.com/gitcoinco/Kudos721Contract) to see this information.

## What is Kudos Direct Send

Kudos Direct Send (KDS) is a direct send of a Kudos ERC 721 NFT from one Ethereum address to another.

## Are Kudos unique

Kudos are semi-fungible tokens.   Each kudos has a limited production run which is designated in the [smart contract](https://github.com/gitcoinco/Kudos721Contract/blob/19b783e50825bfc258179454990a517e84343153/contracts/Kudos.sol#L15) in the `numClonesAllowed` variable..

For example, [this kudos](https://gitcoin.co/kudos/430/resilience) has a total of 200 that will ever be in existence.

When a new kudos is [minted](https://github.com/gitcoinco/Kudos721Contract/blob/19b783e50825bfc258179454990a517e84343153/contracts/Kudos.sol#L48) we create a new *Gen 0 Kudos*.

That *Gen 0 Kudos* can then be [cloned](https://github.com/gitcoinco/Kudos721Contract/blob/19b783e50825bfc258179454990a517e84343153/contracts/Kudos.sol#L68) up to `numClonesAllowed` times, which will create `numClonesAllowed` *Gen 1 Kudos*.

Creating limited production runs of Kudos allows us to manage the unit economics of Kudos.  For example, it costs us $20 to pay our illustrator to create a new piece of artwork.  Nobody is going to pay $20 for a Kudos NFT, so we instead offer a limited production run of 200 Kudos which are priced at $0.40 each.  When that production run sells out, the artist has made gross $40 in revenue, which nets out to $20 in profit.

## What is Kudos Indirect Send?

Kudos Indirect Send (KIS) enables Gitcoin users to send a Kudos to *any github/gitcoin username*.  KIS is effectively a proxy account that can hold a Kudos 721 NFT until a recipient (who is authorized by a github username) claims it.

The Kudos Indirect send architecture diagram is available [here](https://github.com/gitcoinco/web#of-a-tip)

## When is Kudos Indirect Send used and when is Kudos Direct Send Used?

If a user has set a preferred Ethereum address in their [account](https://gitcoin.co/settings/account), KDS will be used.

If not, KIS will be used.

## I have a question that's not listed here

Checkout the Kudos FAQ [here](https://gitcoin.co/kudos/#faq)
