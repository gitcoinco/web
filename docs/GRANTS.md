# Grants General Documentation

grants is built upon [EIP 1337](https://1337alliance.org).

specifically, it is built upon [this smart contract](https://github.com/gitcoinco/grants1337/blob/master/contracts/Subscription.sol) which [was audit'ed by ZKLabs in Q4 2018](https://hackmd.io/s/HJ1QgH8F7).

## How Grants works

When you create a new grant at `/grants/new`, you are deploying a new version of this contract.

When you fund a new grant at `/grants/<pk>/<slug>/fund`, you are `approve()`ing a batch of ERC20 tokens to be sent, and you are signing a message that will be used to create recurring transactions down the line.

How are those transactions created, you say?  Well, it's via a *sub-miner*....

## Sub Miner

The subminer takes the signed message you created in the frontend (see above), and runs `executeSubscription` every *periodSeconds* interval.

Here's what it does in psuedocode:

```python
iterate through all subscriptions:
    contract.methods.getSubscriptionHash(..)
    ready = contract.methods.isSubscriptionReady(..)
    if ready:
        contract.methods.executeSubscription(..)
```

In order to run it, this is what you want to do:

```shell
./manage.py subminer <network> <optional_live_flag>
```

aka

```shell
./manage.py subminer rinkeby --live
```

When you run this code, it looks through all of the active grants on your local on `<network>`, and then runs `executeSubscription()` on them.  if `executeSubscription()` succeeds, it will trigger some other actions (mostly emails, db mutations, etc)

Heres an example successful tx created by the subminer: https://rinkeby.etherscan.io/tx/0x274c159a6d89513c3f0b533a5329bef4ce02b3ffc770bece9a8ce5d269319f72

## More information

For more information on the subminer for grants, checkout

* https://github.com/gitcoinco/web/issues/2424
* https://github.com/gitcoinco/web/pull/3055
* https://gitcoin.co/slack
* http://1337alliance.com
