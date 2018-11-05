
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


