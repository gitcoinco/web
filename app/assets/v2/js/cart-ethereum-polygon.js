
Vue.component('grantsCartEthereumPolygon', {
  props: {
    currentTokens: { type: Array, required: true }, // Array of available tokens for the selected web3 network
    donationInputs: { type: Array, required: true }, // donationInputs computed property from cart.js
    grantsByTenant: { type: Array, required: true }, // Array of grants in cart
    maxCartItems: { type: Number, required: true }, // max number of items in cart
    network: { type: String, required: true }, // web3 network to use
    grantsUnderMinimalContribution: { type: Array, required: true } // Array of grants under min contribution
  },

  data: function() {
    return {
      polygon: {
        showModal: false, // true to show modal to user, false to hide
        checkoutStatus: 'not-started' // options are 'not-started', 'pending', and 'complete'
      },

      cart: {
        tokenList: [], // array of tokens in the cart
        unsupportedTokens: [] // tokens in cart which are not supported by zkSync
      },

      user: {
        address: undefined, // connected web3 wallet address
        hasEnoughBalance: true
      }
    };
  },

  mounted() {
    // If user started checking out with zkSync, warn them before closing or reloading page. Note
    // that beforeunload may sometimes be ignored by browsers, e.g. if users have not interacted
    // with the page. This shows a generic message staying "Leave site? Changes you made may not be
    // saved". The ability to change this message was removed by browsers as it's widely considered
    // a security issue. Source: https://stackoverflow.com/questions/40570164/how-to-customize-the-message-changes-you-made-may-not-be-saved-for-window-onb
    window.addEventListener('beforeunload', (e) => {
      // The below message will likely be ignored as explaned above, but we include it just in case
      if (this.polygon.checkoutStatus === 'pending') {
        e.returnValue = 'Polygon checkout in progress. Are you sure you want to leave?';
      }
    });

    // Update Polygon checkout connection, state, and data frontend needs when wallet connection changes
    window.addEventListener('dataWalletReady', async(e) => {
      await this.setupPolygon();
      await this.onChangeHandler(this.donationInputs);
    });
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
    }
  },

  watch: {
    // Watch donationInputs prop so we can update cart.js as needed on changes
    donationInputs: {
      immediate: true,
      async handler(donations) {
        // Setup polygon (e.g. when mounted)
        await this.setupPolygon();
        // Update state and data that frontend needs
        await this.onChangeHandler(donations);
      }
    },

    // When network changes we need to update Polygon config, fetch new balances, etc.
    network: {
      immediate: true,
      async handler() {
        await this.setupPolygon();
        await this.onChangeHandler(this.donationInputs);
      }
    }
  },

  methods: {
    // Use the same error handler used by cart.js
    handleError(e) {
      appCart.$refs.cart.handleError(e);
    },

    // We want to run this whenever wallet or cart content changes
    async onChangeHandler(donations) {
      // Get array of token symbols based on cart data. For example, if the user has two
      // DAI grants and one ETH grant in their cart, this returns `[ 'DAI', 'ETH' ]`
      this.cart.tokenList = [...new Set(donations.map((donation) => donation.name))];

      // Get list of tokens in cart not supported by zkSync
      this.cart.unsupportedTokens = this.cart.tokenList.filter(
        (token) => !this.supportedTokens.includes(token)
      );

      // Check if user has enough balance and update this.user.hasEnoughBalance + use insufficientBalanceAlert()

      // Update the fee estimate and gas cost based on changes
      const estimatedGasCost = this.estimateGasCost();

      // Emit event so cart.js can update state accordingly to display info to user
      this.$emit('polygon-data-updated', {
        polygonUnsupportedTokens: this.cart.unsupportedTokens,
        polygonEstimatedGasCost: estimatedGasCost
      });
    },

    // Alert user they have insufficient balance to complete checkout
    insufficientBalanceAlert() {
      this.polygon.showModal = false; // hide checkout modal if visible
      this.resetPolygonModal(); // reset modal settings
      this.handleError(new Error('Insufficient balance to complete checkout')); // throw error and show to user
    },

    // Reset Polygon modal status after a checkout failure
    resetPolygonModal() {
      this.polygon.checkoutStatus = 'not-started';
    },

    async setupPolygon() {
      // Connect to Polygon network with MetaMask
      try {
        this.user.address = await ethereum.request({ method: 'eth_requestAccounts' })[0];
        await ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: '0x13881' }] // Mainnet - 0x89
        });
      } catch (switchError) {
        // This error code indicates that the chain has not been added to MetaMask
        if (switchError.code === 4902) {
          try {
            await ethereum.request({
              method: 'wallet_addEthereumChain',
              params: [{
                chainId: '0x13881',
                rpcUrls: ['https://rpc-mumbai.maticvigil.com'],
                chainName: 'Matic Testnet',
                nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 }
              }]
            });
          } catch (addError) {
            if (addError.code === 4001) {
              _alert({ message: gettext('Please connect MetaMask to Polygon network.') }, 'danger');
            } else {
              console.error(addError);
            }
          }
        } else if (switchError.code === 4001) {
          // this.handleError(new Error('Please connect MetaMask to Polygon network.'));
          _alert({ message: gettext('Please connect MetaMask to Polygon network.') }, 'danger');
        } else {
          console.error(switchError);
        }
      }
    },

    // Send a batch transfer based on donation inputs
    async checkoutWithPolygon() {
      try {
        this.user.address = await appCart.$refs.cart.initializeStandardCheckout();

        // TODO: Make sure network is
        const isCorrectNetwork = null;

        // Token approvals and balance checks from bulk checkout contract
        // (just checks data, does not execute approvals)
        const allowanceData = await appCart.$refs.cart.getAllowanceData(
          this.user.address, '0x3E2849E2A489C8fE47F52847c42aF2E8A82B9973'
        );

        // Save off cart data
        this.polygon.checkoutStatus = 'pending';

        // TODO: Prompt user to complete checkout
        const txHash = null;

        // Save contributors to database and redirect to success modal
        console.log('Transaction hash: ', txHash);
        _alert('Saving contributions. Please do not leave this page.', 'success', 200);
        await appCart.$refs.cart.postToDatabase(
          txHash, // array of transaction hashes for each contribution
          null, // TODO: this.zksync.contractAddress, // we use the zkSync mainnet contract address to represent zkSync deposits
          this.user.address
        );
        this.polygon.checkoutStatus = 'complete'; // allows user to freely close tab now
        await appCart.$refs.cart.finalizeCheckout(); // Update UI and redirect

      } catch (e) {
        switch (e) {
          case 'User closed zkSync':
            _alert('Checkout not complete: User closed the zkSync page. Please try again', 'danger');
            this.resetZkSyncModal();
            throw e;

          case 'Failed to open zkSync page':
            _alert('Checkout not complete: Unable to open the zkSync page. Please try again', 'danger');
            this.resetZkSyncModal();
            throw e;

          case 'Took too long for the zkSync page to open':
            _alert('Checkout not complete: Took too long to open the zkSync page. Please try again', 'danger');
            this.resetZkSyncModal();
            throw e;

          default:
            this.handleError(e);
        }
      }
    },

    // Estimates the total gas cost of a zkSync checkout and sends it to cart.js
    estimateGasCost() {
      // Estimate minimum gas cost based on 550 gas per transfer
      const gasPerTransfer = toBigNumber('550'); // may decrease as low as 340 as zkSync gets more traction
      const numberOfTransfers = String(this.donationInputs.length);
      const minimumCost = gasPerTransfer.mul(numberOfTransfers);
      let totalCost = minimumCost;

      // If user has enough balance within zkSync, cost equals the minimum amount
      const { isBalanceSufficient, requiredAmounts } = this.hasEnoughBalanceInZkSync();

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
    hasEnoughBalanceInZkSync() {
      const zksyncBalances = this.user.zksyncState.committed.balances; // object, keys are token symbols, values are token balances as string
      const requiredAmounts = {}; // keys are token symbols, values are required amounts as BigNumber

      // Get total amount needed for eack token by summing over donation inputs
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
