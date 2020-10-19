Vue.component('grantsCartEthereumZksync', {
  props: {
    currentTokens: { type: Array, required: true }, // Array of available tokens for the selected web3 network
    donationInputs: { type: Array, required: true }, // donationInputs computed property from cart.js
    network: { type: String, required: true } // web3 network to use
  },
  template: `
    <button class="btn btn-gc-blue button--full shadow-none py-3 mt-1" id='js-zkSyncfundGrants-button' @click="checkoutWithZksync">
      Checkout with zkSync
    </button>
  `,
  data: function() {
    return {
      // Constants
      constants: {
        ETH_ADDRESS: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
      },

      // Contract information
      contracts: {
        batchZksyncDeposit: {
          address: '0x9D37F793E5eD4EbD66d62D505684CD9f756504F6', // same on mainnet and Rinkeby
          abi:
            '[{"inputs":[{"internalType":"address","name":"_zkSync","type":"address"},{"internalType":"contract IERC20[]","name":"_tokens","type":"address[]"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"contract IERC20","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"AllowanceSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"contract IERC20","name":"token","type":"address"},{"indexed":true,"internalType":"uint104","name":"amount","type":"uint104"},{"indexed":true,"internalType":"address","name":"user","type":"address"}],"name":"DepositMade","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[],"name":"ETH_TOKEN_PLACHOLDER","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"},{"components":[{"internalType":"contract IERC20","name":"token","type":"address"},{"internalType":"uint104","name":"amount","type":"uint104"}],"internalType":"struct BatchZkSyncDeposit.Deposit[]","name":"_deposits","type":"tuple[]"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"setAllowance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"zkSync","outputs":[{"internalType":"contract IZkSync","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'
        },
        zksync: {
          address: '0xaBEA9132b05A70803a4E85094fD0e1800777fBEF', // default to mainnet address
          abi:
            '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockVerification","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"totalBlocksVerified","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"totalBlocksCommitted","type":"uint32"}],"name":"BlocksRevert","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"DepositCommit","type":"event"},{"anonymous":false,"inputs":[],"name":"ExodusMode","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint32","name":"nonce","type":"uint32"},{"indexed":false,"internalType":"bytes","name":"fact","type":"bytes"}],"name":"FactAuth","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"FullExitCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint64","name":"serialId","type":"uint64"},{"indexed":false,"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"indexed":false,"internalType":"bytes","name":"pubData","type":"bytes"},{"indexed":false,"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"name":"NewPriorityRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"},{"indexed":true,"internalType":"address","name":"owner","type":"address"}],"name":"OnchainDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"OnchainWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsAdd","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsComplete","type":"event"},{"constant":true,"inputs":[],"name":"EMPTY_STRING_KECCAK","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"authFacts","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes22","name":"","type":"bytes22"}],"name":"balancesToWithdraw","outputs":[{"internalType":"uint128","name":"balanceToWithdraw","type":"uint128"},{"internalType":"uint8","name":"gasReserveValue","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"blocks","outputs":[{"internalType":"uint32","name":"committedAtBlock","type":"uint32"},{"internalType":"uint64","name":"priorityOperations","type":"uint64"},{"internalType":"uint32","name":"chunks","type":"uint32"},{"internalType":"bytes32","name":"withdrawalsDataHash","type":"bytes32"},{"internalType":"bytes32","name":"commitment","type":"bytes32"},{"internalType":"bytes32","name":"stateRoot","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint64","name":"_n","type":"uint64"}],"name":"cancelOutstandingDepositsForExodusMode","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint32","name":"_feeAccount","type":"uint32"},{"internalType":"bytes32[]","name":"_newBlockInfo","type":"bytes32[]"},{"internalType":"bytes","name":"_publicData","type":"bytes"},{"internalType":"bytes","name":"_ethWitness","type":"bytes"},{"internalType":"uint32[]","name":"_ethWitnessSizes","type":"uint32[]"}],"name":"commitBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_n","type":"uint32"}],"name":"completeWithdrawals","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint104","name":"_amount","type":"uint104"},{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositETH","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"uint16","name":"_tokenId","type":"uint16"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"}],"name":"exit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"},{"internalType":"uint16","name":"","type":"uint16"}],"name":"exited","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"exodusMode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPendingWithdrawalIndex","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPriorityRequestId","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"address","name":"_token","type":"address"}],"name":"fullExit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"_address","type":"address"},{"internalType":"uint16","name":"_tokenId","type":"uint16"}],"name":"getBalanceToWithdraw","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"getNoticePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"initializationParameters","type":"bytes"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"isReadyForUpgrade","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"numberOfPendingWithdrawals","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"pendingWithdrawals","outputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint16","name":"tokenId","type":"uint16"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"priorityRequests","outputs":[{"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"internalType":"bytes","name":"pubData","type":"bytes"},{"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_maxBlocksToRevert","type":"uint32"}],"name":"revertBlocks","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"_pubkey_hash","type":"bytes"},{"internalType":"uint32","name":"_nonce","type":"uint32"}],"name":"setAuthPubkeyHash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksCommitted","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksVerified","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalCommittedPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalOpenPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"triggerExodusIfNeeded","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"upgradeParameters","type":"bytes"}],"name":"upgrade","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeCanceled","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeFinishes","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeNoticePeriodStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActivationTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"upgradePreparationStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"},{"internalType":"bytes","name":"_withdrawalsData","type":"bytes"}],"name":"verifyBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint128","name":"_maxAmount","type":"uint128"}],"name":"withdrawERC20Guarded","outputs":[{"internalType":"uint128","name":"withdrawnAmount","type":"uint128"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawETH","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]',
          addressMainnet: '0xaBEA9132b05A70803a4E85094fD0e1800777fBEF',
          addressRinkeby: '0x82F67958A5474e40E1485742d648C0b0686b6e5D'
        }
      },

      // User web3 info
      user: {
        address: this.userAddress,
        ethersProvider: undefined,
        signer: undefined
      },

      // zkSync SDK parameters
      zksync: {
        provider: undefined,
        numberOfConfirmationsNeeded: undefined,
        wallet: undefined,
        walletState: undefined
      }
    };
  },

  watch: {
    network: function(newNetworkName) {
      // Update properties dependent on user's web3 network
      this.contracts.zksync.address =
        newNetworkName === 'rinkeby'
          ? this.contracts.zksync.addressRinkeby
          : this.contracts.zksync.addressMainnet;
    }
  },

  computed: {
    supportedTokens() {
      const mainnetTokens = [ 'ETH', 'DAI', 'USDC', 'USDT', 'LINK', 'WBTC', 'PAN', 'SNT' ];

      return this.network === 'rinkeby' ? [ 'ETH', 'USDT', 'LINK' ] : mainnetTokens;
    }
  },

  methods: {
    /**
     * @notice Gets the user's address from the currently connected wallet
     */
    async getUserAddress() {
      return (await web3.eth.getAccounts())[0];
    },

    /**
     * @notice Called on page load to initialize zkSync
     */
    async setupZkSync() {
      this.user.address = await this.getUserAddress();
      this.user.ethersProvider = new ethers.providers.Web3Provider(provider); // provider is a global
      this.user.signer = this.user.ethersProvider.getSigner();

      this.zksync.provider = await zksync.getDefaultProvider(this.network, 'HTTP');
      this.zksync.numberOfConfirmationsNeeded = await this.zksync.provider.getConfirmationsForEthOpAmount();
      this.zksync.state = await this.zksync.provider.getState(this.user.address);
    },

    /**
     * @notice Logs the user in to zkSync and registers their account if needed
     */
    async loginToZkSync() {
      this.zksync.wallet = await zksync.Wallet.fromEthSigner(this.user.signer, this.user.ethersProvider);
      await this.checkAndRegisterSigningKey();
    },

    /**
     * @notice For the user's zkSync wallet, checks if the public key needs to be registered, and
     * if so registers it
     * @dev Must be called after the user has logged in to zkSync
     */
    async checkAndRegisterSigningKey() {
      // To control assets in zkSync network, an account must register a separate public key
      // once. This can only be done once they have interacted with the network in some way, such
      // as receiving a deposit, so we do that now since the deposit is complete. It cannot be
      // done earlier because otherwise the account won't exist in the zkSync accounts Merkle tree
      console.log('Registering public key to unlock deterministic wallet on zkSync...');
      const syncWallet = this.zksync.wallet;

      if (await syncWallet.isSigningKeySet()) {
        console.log('✅  Sync wallet was already initialized');
        return;
      }
      
      // This means the account has never interacted with the network
      if ((await syncWallet.getAccountId()) == undefined)
        throw new Error('Unknown account');
      
      // Get the first token listed and use that to pay for signing key transaction
      const tokensInWallet = Object.keys(this.zksync.state.committed.balances);
      const feeToken = tokensInWallet[0];

      // Determine how to set key based on wallet type
      let changePubkey;

      if (syncWallet.ethSignerType.verificationMethod === 'ECDSA') {
        console.log('  Using ECDSA to set signing key');
        changePubkey = await syncWallet.setSigningKey({ feeToken });
      } else {
        console.log('  Using ERC-1271 to set signing key. This requires an on-chain transaction');
        await syncWallet.onchainAuthSigningKey();
        changePubkey = await syncWallet.setSigningKey({ feeToken, onchainAuth: true });
      }

      // Wait until the tx is committed
      console.log('Signing key set, waiting for transaction receipt');
      await changePubkey.awaitReceipt();
      console.log('✅ specified sync wallet is ready to use on zkSync');
    },

    /**
     * @notice Sends all donations from the user's zkSync account to the grant owners
     */
    async finishZkSyncTransfers() {
      try {
        // Send batch transfers
        //   TODO

        console.log('✅✅✅ Checkout complete!');

        // Final processing
        //   TODO await this.setInterruptStatus(null, this.userAddress);
        //   TODO await this.finalizeCheckout();
      } catch (e) {
        this.handleError(e);
      }
    },

    /**
     * @notice Initializes the zkSync checkout process
     */
    async checkoutWithZksync() {
      console.log('checkout starting!');
      await this.loginToZkSync();
      console.log('checkout completed!');
    }
  },

  async mounted() {
    console.log('mounted hook started');
    await this.setupZkSync();
    console.log('mounted hook done');
  }
});
