# Grants General Documentation

## Rounds 6+

In round 6 we transitioned away from the [EIP 1337](https://1337alliance.org) contract and replaced
it with a single contract that enables bulk donations for all grants. The source of this `BulkCheckout` contract
can be found [here](https://github.com/gitcoinco/BulkTransactions/blob/master/contracts/BulkCheckout.sol),
and it has been deployed to the mainnet at
[0x7d655c57f71464B6f83811C55D84009Cd9f5221C](https://etherscan.io/address/0x7d655c57f71464B6f83811C55D84009Cd9f5221C).
It works as follows:

1. Instead of funding each grant individually, grants are now added to your cart
2. For each grant in your cart, you select the token and amount you want to donate
3. Upon checking out, all donations are handled in a single transaction thanks to the `BulkCheckout` contract.
4. This contract has one main function, `donate()` which takes an array of structs.
5. Each struct contains all information required for a donation—the token to donate with, the amount to donate, and the grant to donate to
6. Prior to calling this function, the Gitcoin frontend will ensure you have approved the `BulkCheckout` contract to spend your tokens. If you haven't, you will be prompted to confirm an approval transaction for the exact amount to be donated. You are free to adjust the approval amount to remove the need to re-approve the contract in subsequent donations.
7. After the approval transactions are submitted, the bulk checkout transaction is submitted through the `donate()` function.

## Rounds 1–5

grants is built upon [EIP 1337](https://1337alliance.org).

specifically, it is built upon [this smart contract](https://github.com/gitcoinco/grants1337/blob/master/contracts/Subscription.sol) which [was audit'ed by ZKLabs in Q4 2018](https://hackmd.io/s/HJ1QgH8F7).

### How Grants works

When you create a new grant at `/grants/new`, you are deploying a new version of this contract.

When you fund a new grant at `/grants/<pk>/<slug>/fund`, you are `approve()`ing a batch of ERC20 tokens to be sent, and you are signing a message that will be used to create recurring transactions down the line.

How are those transactions created, you say? Well, it's via a _sub-miner_....

### Sub Miner

The subminer takes the signed message you created in the frontend (see above), and runs `executeSubscription` every _periodSeconds_ interval.

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

When you run this code, it looks through all of the active grants on your local on `<network>`, and then runs `executeSubscription()` on them. if `executeSubscription()` succeeds, it will trigger some other actions (mostly emails, db mutations, etc)

Heres an example successful tx created by the subminer: https://rinkeby.etherscan.io/tx/0x274c159a6d89513c3f0b533a5329bef4ce02b3ffc770bece9a8ce5d269319f72

### More information

For more information on the subminer for grants, checkout

- https://github.com/gitcoinco/web/issues/2424
- https://github.com/gitcoinco/web/pull/3055
  https://chat.gitcoin.co/
- http://1337alliance.com
