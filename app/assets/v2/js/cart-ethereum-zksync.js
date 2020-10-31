const { getAddress } = ethers.utils;

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
      zksync: {
        checkoutManager: undefined, // zkSync API CheckoutManager class
        feeTokenName: undefined, // token name, e.g. ETH
        feeTokenAmount: undefined // fee amount denominated in feeTokenName
      },

      // User web3 info
      user: {
        address: undefined, // connected web3 wallet address
        zkSyncState: undefined // contains account balances of zkSync wallet
      },

      // zkSync checkout fee parameters
      fee: {
        tokenName: undefined, // token name, e.g. ETH
        amount: undefined // denominated in the token name
      }
    };
  },

  computed: {
    // Returns an array of token symbols based on the items in the cart. If the user has two DAI
    // grants and one ETH grant, this returns ['DAI', 'ETH']
    selectedTokens() {
      return [...new Set(this.donationInputs.map((donation) => donation.name))];
    },

    /**
     * @dev List of tokens supported by zkSync + Gitcoin. To add a token to this list:
     *   1. Make sure the token is supported by zkSync
     *        Mainnet list: https://api.zksync.io/api/v0.1/tokens
     *        Rinkeby list: https://rinkeby-api.zksync.io/api/v0.1/tokens
     *   2. Add the token symbol to the appropriate list below
     * @dev We hardcode the list here instead of fetching from the API to improve performance and
     * reduce problems that arise if zkSync's server is slow
     */
    supportedTokens() {
      const mainnetTokens = [ 'ETH', 'DAI', 'USDC', 'TUSD', 'USDT', 'SUSD', 'BUSD', 'LEND', 'BAT', 'KNC', 'LINK', 'MANA', 'MKR', 'REP', 'SNX', 'WBTC', 'ZRX', 'MLTT', 'LRC', 'HEX', 'PAN', 'SNT', 'YFI', 'UNI', 'STORJ', 'TBTC', 'EURS', 'GUSD', 'RENBTC', 'RNDR', 'DARK', 'CEL', 'AUSDC', 'CVP', 'BZRX', 'REN' ];
      const rinkebyTokens = [ 'ETH', 'USDT', 'USDC', 'LINK', 'TUSD', 'HT', 'OMG', 'TRB', 'ZRX', 'BAT', 'REP', 'STORJ', 'NEXO', 'MCO', 'KNC', 'LAMB', 'GNT', 'MLTT', 'XEM', 'DAI', 'PHNX' ];

      return this.network === 'rinkeby' ? rinkebyTokens : mainnetTokens;
    },

    // Returns true if all tokens in the cart support zkSync, false otherwise
    canUseZksync() {
      const unsupportedTokens = this.selectedTokens.filter((token) => !this.supportedTokens.includes(token));

      return unsupportedTokens.length === 0; // if there are no unsupported tokens, zksync checkout is supported
    },

    // Array of transfer objects in the format zkSync needs
    transfers() {
      // Generate array of objects used to send the transfer. We give each transfer a fee of zero,
      // then zkSync will append one more zero-value transfer that covers the full fee
      return this.donationInputs.map((donation) => {
        return {
          to: getAddress(donation.dest), // ensure we use a checksummed address
          token: donation.name, // token symbol
          amount: donation.amount,
          semanticType: 'Transaction'
        };
      });
    }
  },

  methods: {
    // Error handler used by cart.js
    handleError(e) {
      appCart.$refs.cart.handleError(e);
    },

    // Called on page load to initialize zkSync
    async setupZkSync() {
      this.user.address = (await web3.eth.getAccounts())[0];
      this.zksync.checkoutManager = new ZkSyncCheckout.CheckoutManager(this.network);
      this.user.zksyncState = await this.zksync.checkoutManager.getState(this.user.address);
    },


    // Returns fee estimate for the items in their cart, as a string, in units of feeToken
    async getFeeEstimate() {
      // TODO for now just use the token of the first one as the fee token
      this.zksync.feeTokenName = this.transfers[0].token;
      this.zksync.feeTokenAmount = await this.zksync.checkoutManager.estimateBatchFee(
        this.transfers,
        this.zksync.feeTokenName
      );
    },

    /**
     * @notice Send a batch transfer based on donation inputs
     */
    async checkoutWithZksync() {
      try {
        // Get fee estimate and send user to zkSync to complete checkout
        await this.getFeeEstimate();
        const txHashes = await this.zksync.checkoutManager.zkSyncBatchCheckout(
          this.transfers,
          this.zksync.feeTokenName
        );
        
        // Save contributors to database and redirect to success modal
        _alert('Saving contributions. Please do not leave this page.', 'success', 2000);
        // TODO save contributions to database ------------------------
        await appCart.$refs.cart.finalizeCheckout(); // Update UI and redirect

      } catch (e) {
        switch (e) {
          case 'User closed zkSync':
            _alert('Checkout not complete: User closed the zkSync page', 'error');
            throw e;

          case 'Failed to open zkSync page':
            _alert('Unable to open the zkSync page. Please try again', 'error');
            throw e;

          case 'Took too long for the zkSync page to open':
            _alert('Took too long to open the zkSync page. Please try again', 'error');
            throw e;

          default:
            this.handleError(e);
        }
      }
    }
  },

  async mounted() {
    console.log('mounted hook started');
    await this.setupZkSync();
    console.log('mounted hook done');
  }
});
