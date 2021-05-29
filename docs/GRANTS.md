# Grants General Documentation

- [Grants General Documentation](#grants-general-documentation)
  - [Round 8](#round-8)
  - [Round 7](#round-7)
    - [Architecture Background](#architecture-background)
    - [Checkout Flow](#checkout-flow)
    - [Transfer Fees](#transfer-fees)
  - [Round 6](#round-6)
  - [Rounds 1–5](#rounds-15)
    - [How Grants works](#how-grants-works)
    - [Sub Miner](#sub-miner)
    - [More information](#more-information)

## Round 8

In round 8, the zkSync checkout flow was significantly simplified thanks to the new
[`zksync-checkout`](https://www.npmjs.com/package/zksync-checkout) library released by zkSync. This library natively supports batch transfers, meaning multiple transfers can be approved
with just one L1 signature. This provides many benefits over the round 7 approach:

- It resolves the UX issues we worked around by introducing "Gitcoin zkSync wallets" in round 7
- Security is improved, as Gitcoin never sees any of your zkSync private keys
- It provides a familiar web2 checkout flow, similar to "Checkout with Amazon" or "Checkout with Google Pay"
- It's less confusing to users as your transaction history on zkScan now shows ordinary transfers to grants instead of one big transfer to an unknown address
- These native batch transfers are atomic, so your checkout will either succeed or fail. The previous approach can leave user accounts in an odd state if one of the multiple transfers failed, and care must be taken to properly recover from this

For more information on how this new checkout flow works, please see the
[zkSync Checkout documentation](https://www.notion.so/zkSync-Checkout-docs-2bffd6f169e746d0b51873e4127992a6).

## Round 7

In round 7 we introduced the option to checkout on L2 using [zkSync](https://zksync.io/).
This means there are now three possible checkout flows&mdash;the Bulk Checkout flow introduced in
Round 6, and two zkSync checkout flows.

### Architecture Background

Before describing these two flows, we'll review how zkSync accounts work at a high level. When
logging in to your zkSync account, such as at https://wallet.zksync.io/, you are asked to sign a
message. That signature is used to generate a private key, and each transfer then requires two
signatures&mdash;one from this private key, and as an additional security measure, one more from
your regular web3 wallet. This is great from a security perspective, but not so great from a UX
perspective. Requiring one signature for each transfer can be a pain if you want to send a lot of
transfers, so you'd be doing a lot of clicking when checking out with large carts.

To remedy this, we ask you to login to a "Gitcoin zkSync" account. This generates an L1 account
that the Gitcoin frontend can use to sign transactions directly. The private key to this account is
derived from the signature, and is never stored or transmitted anywhere. We then login to zkSync with *this account*, and now
can use this account to send transfers without prompting you for each transfer! Funds are
only held by this account temporarily to improve UX. Because it does not permanently hold funds
there is no additional security risk.

### Checkout Flow

Based on the items in your cart, we check your zkSync balances to see if you already have enough
funds on zkSync to complete checkout.

If you do, the checkout flow is as follows:

1. Sign a message to login to your Gitcoin zkSync account
2. Sign a message to login to your regular zkSync account
3. Sign a message to transfer funds from your regular zkSync account to your Gitcoin zkSync account

Step 3 is repeated for each token you are donating. If you only are using DAI, step 3 will ask
for one signature. If you are donating DAI and ETH, it will ask for two signatures.

After those signatures are received, the transfers are executed so the funds are in your Gitcoin
zkSync account. From there, all transfers of funds to grant owners are fired off in a rapid process
that only takes a few  seconds. Any leftover funds in the Gitcoin zkSync account (typically due to
our conservative estimates of what zkSync trasfer fees will be) are transferred back to your regular
zkSync account so you can access them at https://wallet.zksync.io/.

If you do not have enough funds in your zkSync account to complete checkout, the flow is as follows:

1. Sign a message to login to your Gitcoin zkSync account
2. Confirm one transaction for each required ERC20 approval (~25k–50k gas)
3. Confirm one transaction to deposit funds into zkSync (~180k–200k gas)

If you are only donating with one token, step 3 calls the deposit function directly on the
[zkSync contract](https://etherscan.io/address/0xabea9132b05a70803a4e85094fd0e1800777fbef). If you
are donating with multiple tokens, step 3 uses our
[Batch ZkSync Deposit Contract](https://github.com/gitcoinco/BulkTransactions/blob/master/contracts/BatchZkSyncDeposit.sol)
to reduce both the number of transactions and the gas costs for multiple deposits.

Funds are deposited directly to your Gitcoin zkSync account. To ensure your deposit is not reverted, it
takes 10 confirmations for your deposit to be accepted by zkSync. After waiting for those 10 confirmations,
we converge on the above flow, so all transfers of funds to grant owners are now executed. Again,
any leftover funds in the Gitcoin zkSync account (in this case, this includes any additional funds
you elected to deposit into zkSync) are transferred back to your regular zkSync account.

### Transfer Fees

zkSync transfer costs can be found in their [documentation](https://zksync.io/faq/tokens.html#fee-costs).
Right now it costs about 2k gas per transfer, compared to ~60k gas to transfer DAI on L1, and
~180k gas to deposit funds into zkSync. Once zkSync 1.1 is released, these transfer fees will be
reduced to about 400 gas per transfer.

These transfers support what zkSync calls [gasless meta-transactions](https://zksync.io/faq/tokens.html#how-fees-are-payed),
where all transaction fees are paid in the token being transferred. For example, if you want to
transfer 5 DAI, there may be a fee of, say, 0.10 DAI, resulting in a total cost of 5.10 DAI.

When checking out with Gitcoin grants, fees are additive. If you have 20 DAI in your cart, the
total cost will be 20 DAI plus transaction fees. Transfers to new recipients in zkSync cost
more than transfers to users who have previously used zkSync. Gitcoin takes a conservative approach
and assumes all transfers are to new users to ensure you don't run out of fees when transferring
funds. As a result, the "Estimated fees" shown are checkout may be much higher than
the actual fees you will pay. Any leftover fees are transferred from your Gitcoin zkSync account
back to your regular zkSync account.

## Round 6

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
  https://discord.gg/gitcoin
- http://1337alliance.com
