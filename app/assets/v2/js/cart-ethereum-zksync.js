const { getAddress } = ethers.utils;

Vue.component('grantsCartEthereumZksync', {
  props: {
    currentTokens: { type: Array, required: true }, // Array of available tokens for the selected web3 network
    donationInputs: { type: Array, required: true }, // donationInputs computed property from cart.js
    network: { type: String, required: true } // web3 network to use
  },

  template: `
    <button 
      @click="checkoutWithZksync"
      class="btn btn-gc-blue button--full shadow-none py-3 mt-1"
      :disabled="zksync.unsupportedTokens.length > 0"
      id='js-zkSyncfundGrants-button'
    >
      Checkout with zkSync
    </button>
  `,

  data: function() {
    return {
      zksync: {
        checkoutManager: undefined, // zkSync API CheckoutManager class
        feeTokenName: undefined, // token name, e.g. ETH
        feeTokenAmount: undefined, // fee amount denominated in feeTokenName
        unsupportedTokens: [] // tokens in cart which are not supported by zkSync
      },

      user: {
        address: undefined, // connected web3 wallet address
        zkSyncState: undefined // contains account balances of zkSync wallet
      }
    };
  },

  computed: {
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

  watch: {
    // Watch donationInputs prop so we can update cart.js as needed on changes
    donationInputs: {
      immediate: true,
      async handler(donations) {
        // Setup zkSync if necessary (e.g. when mounted)
        if (!this.zksync.checkoutManager) {
          await this.setupZkSync();
        }

        // Get array of token symbols based on cart data. For example, if the user has two
        // DAI grants and one ETH grant in their cart, this returns `[ 'DAI', 'ETH' ]`
        const cartTokens = [...new Set(donations.map((donation) => donation.name))];

        // Get list of tokens in cart not supported by zkSync
        this.zksync.unsupportedTokens = cartTokens.filter((token) => !this.supportedTokens.includes(token));
        
        // Set the cart.js state accordingly so it can show this to the user
        appCart.$refs.cart.zkSyncUnsupportedTokens = this.zksync.unsupportedTokens;

        // Update the fee estimate based on new selections
        await this.getFeeEstimate();
      }
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
      this.zksync.checkoutManager = new ZkSyncCheckout.CheckoutManager(this.network || 'mainnet');
      this.user.zksyncState = await this.zksync.checkoutManager.getState(this.user.address);
    },

    // Returns fee estimate for the items in their cart, as a string, in units of feeToken
    async getFeeEstimate(tokenSymbol = undefined) {
      // If tokens in the cart are unsupported, set values to undefined
      if (this.zksync.unsupportedTokens.length > 0) {
        this.zksync.feeTokenName = undefined;
        this.zksync.feeTokenAmount = undefined;
        return;
      }

      // If no token symbol is provided, use the first one in the cart
      if (!tokenSymbol) {
        this.zksync.feeTokenName = this.transfers[0].token;
      }

      // Now we can get and set the fee estimate
      this.zksync.feeTokenAmount = await this.zksync.checkoutManager.estimateBatchFee(
        this.transfers,
        this.zksync.feeTokenName
      );
    },

    // Send a batch transfer based on donation inputs
    async checkoutWithZksync() {
      try {
        // Send user to zkSync to complete checkout
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
  }
});
