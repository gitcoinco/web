const { getAddress } = ethers.utils;

// Wrapper around ethers.js BigNumber which converts undefined values to zero
const toBigNumber = (value) => {
  if (!value)
    return BigNumber.from('0');
  return BigNumber.from(value);
};

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
      :disabled="cart.unsupportedTokens.length > 0"
      id='js-zkSyncfundGrants-button'
    >
      Checkout with zkSync
    </button>
  `,

  data: function() {
    return {
      zksync: {
        checkoutManager: undefined // zkSync API CheckoutManager class
      },

      cart: {
        tokenList: [], // array of tokens in the cart
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
        this.cart.tokenList = [...new Set(donations.map((donation) => donation.name))];

        // Get list of tokens in cart not supported by zkSync
        this.cart.unsupportedTokens = this.cart.tokenList.filter(
          (token) => !this.supportedTokens.includes(token)
        );
        
        // Update the fee estimate and gas cost based on changes
        const estimatedGasCost = this.estimateGasCost();

        // Emit event so cart.js can update state accordingly to display info to user
        this.$emit('zksync-data-updated', {
          zkSyncUnsupportedTokens: this.cart.unsupportedTokens,
          zkSyncEstimatedGasCost: estimatedGasCost
        });
      }
    }
  },

  methods: {
    // Use the same error handler used by cart.js
    handleError(e) {
      appCart.$refs.cart.handleError(e);
    },

    // Called on page load to initialize zkSync
    async setupZkSync() {
      this.user.address = (await web3.eth.getAccounts())[0];
      this.zksync.checkoutManager = new ZkSyncCheckout.CheckoutManager(this.network || 'mainnet');
      this.user.zksyncState = await this.zksync.checkoutManager.getState(this.user.address);
    },

    // Send a batch transfer based on donation inputs
    async checkoutWithZksync(feeTokenSymbol = undefined) {
      try {
        // Set fee token
        if (!feeTokenSymbol)
          feeTokenSymbol = this.transfers[0].token;

        // Send user to zkSync to complete checkout
        const txHashes = await this.zksync.checkoutManager.zkSyncBatchCheckout(
          this.transfers,
          feeTokenSymbol
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
    },

    // Estimates the total gas cost of a zkSync checkout and sends it to cart.js
    estimateGasCost() {
      // Estimate minimum gas cost based on 400 gas per transfer
      const gasPerTransfer = toBigNumber('400');
      const numberOfTransfers = String(this.donationInputs.length);
      const minimumCost = gasPerTransfer.mul(numberOfTransfers);
      let totalCost = minimumCost;
      
      // If user has enough balance within zkSync, cost equals the minimum amount
      const { isBalanceSufficient, requiredAmounts } = this.hasEnoughBalance();

      if (isBalanceSufficient) {
        return totalCost.toString();
      }

      // If we're here, user needs at least one L1 deposit, so let's calculate the total cost
      this.cart.tokenList.forEach((tokenSymbol) => {
        const zksyncBalance = toBigNumber(this.user.zksyncState.committed.balances[tokenSymbol]);
        
        if (requiredAmounts[tokenSymbol].gt(zksyncBalance)) {
          if (tokenSymbol === 'ETH') {
            totalCost = totalCost.add('200000'); // add 200k gas for ETH deposits
          } else {
            totalCost = totalCost.add('250000'); // add 250k gas for token deposits
          }
        }
      });
      return totalCost.toString();
    },

    // Returns true if user has enough balance within zkSync to avoid L1 deposit, false otherwise
    hasEnoughBalance() {
      // Get object where keys are token symbols and values are token balances
      const zksyncBalances = this.user.zksyncState.committed.balances;
      const zksyncTokens = Object.keys(zksyncBalances);

      // Get total amount needed for eack token by summing over donation inputs
      const requiredAmounts = {}; // keys are token symbols, values are BigNumber

      this.donationInputs.forEach((donation) => {
        const tokenSymbol = donation.name;
        const amount = toBigNumber(donation.amount);

        if (!requiredAmounts[tokenSymbol]) {
          // First time seeing this token, set the field and initial value
          requiredAmounts[tokenSymbol] = amount;
        } else {
          // We've seen this token, so just update the total
          requiredAmounts[tokenSymbol] = requiredAmounts[tokenSymbol].add(amount);
        }
      });

      // Compare amounts needed to balance
      let isBalanceSufficient = true; // initialize output

      this.cart.tokenList.forEach((tokenSymbol) => {
        const userAmount = toBigNumber(zksyncBalances[tokenSymbol]);
        const requiredAmount = requiredAmounts[tokenSymbol];
        
        if (requiredAmount.gt(userAmount))
          isBalanceSufficient = false;
      });

      // Return result and required amounts
      return {
        isBalanceSufficient,
        requiredAmounts
      };
    }
  }
});
