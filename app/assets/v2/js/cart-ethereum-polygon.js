const bulkCheckoutAddressPolygon = '0x3E2849E2A489C8fE47F52847c42aF2E8A82B9973';


Vue.component('grantsCartEthereumPolygon', {
  props: {
    currentTokens: { type: Array, required: true }, // Array of available tokens for the selected web3 network
    donationInputs: { type: Array, required: true }, // donationInputs computed property from cart.js
    grantsByTenant: { type: Array, required: true }, // Array of grants in cart
    maxCartItems: { type: Number, required: true }, // max number of items in cart
    grantsUnderMinimalContribution: { type: Array, required: true } // Array of grants under min contribution
  },

  data: function() {
    return {
      network: 'mainnet',
      polygon: {
        showModal: false, // true to show modal to user, false to hide
        checkoutStatus: 'not-started' // options are 'not-started', 'pending', and 'complete'
      },

      cart: {
        tokenList: [], // array of tokens in the cart
        unsupportedTokens: [] // tokens in cart which are not supported by zkSync
      },

      user: {
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
      const mainnetTokens = [ 'MATIC', 'DAI', 'WETH', 'USDC', 'COMP', 'LEND', 'YFI', 'USDT', 'BUSD', 'MANA', 'WBTC', 'KIWI', 'DUST', 'SPN' ];
      const testnetTokens = [ 'MATIC', 'WETH', 'DAI' ];

      return this.network === 'testnet' ? testnetTokens : mainnetTokens;
    },

    donationInputsNativeAmount() {
      return appCart.$refs.cart.donationInputsNativeAmount;
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
    openBridgeUrl() {
      window.open('https://wallet.matic.network/bridge', '_blank');
      this.polygon.checkoutStatus = 'should-deposit';
    },

    initWeb3() {
      return new Web3('https://rpc-mumbai.maticvigil.com');
    },

    // Use the same error handler used by cart.js
    handleError(e) {
      appCart.$refs.cart.handleError(e);
    },

    getDonationInputs() {
      appCart.$refs.cart.getDonationInputs();
    },

    async postToDatabase(txHash, contractAddress, userAddress) {
      await appCart.$refs.cart.postToDatabase(txHash, contractAddress, userAddress, 'eth_polygon');
    },

    async finalizeCheckout() {
      await appCart.$refs.cart.finalizeCheckout();
    },

    async getAllowanceData(userAddress, targetContract) {
      await appCart.$refs.cart.getAllowanceData(userAddress, targetContract);
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
      const estimatedGasCost = await this.estimateGasCost();

      // Emit event so cart.js can update state accordingly to display info to user
      this.$emit('polygon-data-updated', {
        polygonUnsupportedTokens: this.cart.unsupportedTokens,
        polygonEstimatedGasCost: estimatedGasCost
      });
    },

    // Alert user they have insufficient balance to complete checkout
    insufficientBalanceAlert() {
      this.closePolygonModal();
      this.resetPolygonModal();
      this.handleError(new Error('Insufficient balance to complete checkout')); // throw error and show to user
    },

    // Reset Polygon modal status after a checkout failure
    resetPolygonModal() {
      this.polygon.checkoutStatus = 'not-started';
    },

    closePolygonModal() {
      this.polygon.showModal = false;
    },

    async setupPolygon() {
      // Connect to Polygon network with MetaMask
      try {
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
      this.network = getDataChains(ethereum.networkVersion, 'chainId')[0] && getDataChains(ethereum.networkVersion, 'chainId')[0].network;
    },

    // Send a batch transfer based on donation inputs
    async checkoutWithPolygon() {
      try {
        this.setupPolygon();

        if (typeof ga !== 'undefined') {
          ga('send', 'event', 'Grant Checkout', 'click', 'Person');
        }

        // Throw if invalid Gitcoin contribution percentage
        if (Number(this.gitcoinFactorRaw) < 0 || Number(this.gitcoinFactorRaw) > 99) {
          throw new Error('Gitcoin contribution amount must be between 0% and 99%');
        }
  
        // Throw if there's negative values in the cart
        this.donationInputs.forEach(donation => {
          if (Number(donation.amount) < 0) {
            throw new Error('Cannot have negative donation amounts');
          }
        });

        // Token approvals and balance checks from bulk checkout contract
        // (just checks data, does not execute approvals)
        const allowanceData = await this.getAllowanceData(
          ethereum.selectedAddress, bulkCheckoutAddressPolygon
        );

        // Save off cart data
        this.polygon.checkoutStatus = 'pending';

        if (allowanceData.length === 0) {
          // Send transaction and exit function
          this.sendDonationTx(ethereum.selectedAddress);
          return;
        }

        // Request approvals then send donations ---------------------------------------------------
        await this.requestAllowanceApprovalsThenExecuteCallback(
          allowanceData,
          ethereum.selectedAddress,
          bulkCheckoutAddressPolygon,
          this.sendDonationTx,
          [ethereum.selectedAddress]
        );

      } catch (e) {
        this.handleError(e);
      }
    },

    async sendDonationTx(userAddress) {
      let web3 = this.initWeb3();
      // Get our donation inputs
      const bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddressPolygon);
      const donationInputsFiltered = this.getDonationInputs();

      // Send transaction
      bulkTransaction.methods
        .donate(donationInputsFiltered)
        .send({ from: userAddress, gas: this.donationInputsGasLimitL1, value: this.donationInputsEthAmount })
        .on('transactionHash', async(txHash) => {
          console.log('Donation transaction hash: ', txHash);
          _alert('Saving contributions. Please do not leave this page.', 'success', 2000);
          await this.postToDatabase([txHash], bulkCheckoutAddressPolygon, userAddress); // Save contributions to database
          await this.finalizeCheckout(); // Update UI and redirect
        })
        .on('error', (error, receipt) => {
          // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
          this.handleError(error);
        });
    },

    // Estimates the total gas cost of a polygon checkout and sends it to cart.js
    async estimateGasCost() {
      let web3 = this.initWeb3();
      const bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddressPolygon);
      const donationInputsFiltered = this.getDonationInputs();
      let userAddress = (await web3.eth.getAccounts())[0];

      let totalCost = await bulkTransaction.methods
        .donate(donationInputsFiltered)
        .estimateGas({ from: userAddress, value: this.donationInputsNativeAmount });
      
      return totalCost.toString();
    }
  }
});
