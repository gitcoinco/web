const bulkCheckoutAddressPolygon = appCart.$refs.cart.network === 'mainnet'
  ? '0xb99080b9407436eBb2b8Fe56D45fFA47E9bb8877'
  : '0x3E2849E2A489C8fE47F52847c42aF2E8A82B9973';

function objectMap(object, mapFn) {
  return Object.keys(object).reduce(function(result, key) {
    result[key] = mapFn(object[key]);
    return result;
  }, {});
}

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
      polygon: {
        showModal: false, // true to show modal to user, false to hide
        checkoutStatus: 'not-started', // options are 'not-started', 'pending', and 'complete'
        estimatedGasCost: 65000
      },

      cart: {
        tokenList: [], // array of tokens in the cart
        unsupportedTokens: [] // tokens in cart which are not supported by Polygon
      },

      user: {
        requiredAmounts: null
      }
    };
  },

  mounted() {
    window.addEventListener('beforeunload', (e) => {
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
     * @dev List of tokens supported by Polygon + Gitcoin. To add a token to this list:
     *   1. Make sure the token is top 10 used tokens based on Gitcoin's historical data
     *   2. Confirm the token exists on Polygon's list of supported tokens: https://mapper.matic.today/
     *   2. Add the token symbol to the appropriate list below
     * @dev We hardcode the list from Gitcoin's historical data based on the top ten tokens
     *   on ethereum chain and also Polygon network used by users to checkout
     */
    supportedTokens() {
      const mainnetTokens = [ 'DAI', 'ETH', 'USDT', 'USDC', 'PAN', 'BNB', 'UNI', 'CELO', 'MASK', 'MATIC' ];
      const testnetTokens = [ 'DAI', 'ETH', 'USDT', 'USDC', 'UNI', 'MATIC' ];

      return appCart.$refs.cart.network === 'mainnet' ? mainnetTokens : testnetTokens;
    },

    donationInputsNativeAmount() {
      return appCart.$refs.cart.donationInputsNativeAmount;
    },

    requiredAmountsString() {
      let string = '';

      requiredAmounts = this.user.requiredAmounts;
      Object.keys(requiredAmounts).forEach(key => {
        // Round to 2 digits
        if (requiredAmounts[key]) {
          const amount = requiredAmounts[key];
          const formattedAmount = amount.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          });

          if (string === '') {
            string += `${formattedAmount} ${key}`;
          } else {
            string += ` + ${formattedAmount} ${key}`;
          }
        }
      });
      return string;
    }
  },

  watch: {
    // Watch donationInputs prop so we can update cart.js as needed on changes
    donationInputs: {
      immediate: true,
      async handler(donations) {
        // Update state and data that frontend needs
        await this.onChangeHandler(donations);
      }
    },

    // When network changes we need to update Polygon config, fetch new balances, etc.
    network: {
      immediate: true,
      async handler() {
        await this.onChangeHandler(this.donationInputs);
      }
    }
  },

  methods: {
    initWeb3() {
      let url;

      if (appCart.$refs.cart.network === 'mainnet') {
        appCart.$refs.cart.networkId = '137';
        url = 'https://rpc-mainnet.maticvigil.com';
      } else {
        appCart.$refs.cart.networkId = '80001';
        appCart.$refs.cart.network = 'testnet';
        url = 'https://rpc-mumbai.maticvigil.com';
      }

      return new Web3(url);
    },

    openBridgeUrl() {
      let url = appCart.$refs.cart.network == 'mainnet'
        ? 'https://wallet.matic.network/bridge'
        : 'https://wallet.matic.today/bridge';

      window.open(url, '_blank');
      this.polygon.checkoutStatus = 'depositing';
    },

    handleError(e) {
      appCart.$refs.cart.handleError(e);
    },

    getDonationInputs() {
      return appCart.$refs.cart.getDonationInputs();
    },

    getTokenByName(name) {
      return appCart.$refs.cart.getTokenByName(name, true);
    },

    async postToDatabase(txHash, contractAddress, userAddress) {
      await appCart.$refs.cart.postToDatabase(txHash, contractAddress, userAddress, 'eth_polygon');
    },

    async finalizeCheckout() {
      await appCart.$refs.cart.finalizeCheckout();
    },

    async getAllowanceData(userAddress, targetContract) {
      return await appCart.$refs.cart.getAllowanceData(userAddress, targetContract, true);
    },

    async requestAllowanceApprovalsThenExecuteCallback(
      allowanceData, userAddress, targetContract, callback, callbackParams
    ) {
      return await appCart.$refs.cart.requestAllowanceApprovalsThenExecuteCallback(
        allowanceData, userAddress, targetContract, callback, callbackParams
      );
    },

    // We want to run this whenever wallet or cart content changes
    async onChangeHandler(donations) {
      // Get array of token symbols based on cart data. For example, if the user has two
      // DAI grants and one ETH grant in their cart, this returns `[ 'DAI', 'ETH' ]`
      this.cart.tokenList = [...new Set(donations.map((donation) => donation.name))];

      // Get list of tokens in cart not supported by Polygon
      this.cart.unsupportedTokens = this.cart.tokenList.filter(
        (token) => !this.supportedTokens.includes(token)
      );

      // Update the fee estimate and gas cost based on changes
      this.polygon.estimatedGasCost = await this.estimateGasCost();

      // Emit event so cart.js can update state accordingly to display info to user
      this.$emit('polygon-data-updated', {
        polygonUnsupportedTokens: this.cart.unsupportedTokens,
        polygonEstimatedGasCost: this.polygon.estimatedGasCost
      });
    },

    // Reset Polygon modal status after a checkout failure
    resetPolygonModal() {
      this.polygon.checkoutStatus = 'not-started';
    },

    closePolygonModal() {
      this.polygon.showModal = false;
    },

    async setupPolygon() {
      indicateMetamaskPopup();
      // Connect to Polygon network with MetaMask
      const network = appCart.$refs.cart.network;
      let chainId = network === 'mainnet' ? '0x89' : '0x13881';
      let rpcUrl = network === 'mainnet' ? 'https://rpc-mainnet.maticvigil.com'
        : 'https://rpc-mumbai.maticvigil.com';

      try {
        await ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId }]
        });
      } catch (switchError) {
        // This error code indicates that the chain has not been added to MetaMask
        if (switchError.code === 4902) {
          let networkText = network === 'rinkeby' || network === 'goerli' ||
            network === 'ropsten' || network === 'kovan' ? 'testnet' : network;

          try {
            await ethereum.request({
              method: 'wallet_addEthereumChain',
              params: [{
                chainId,
                rpcUrls: [rpcUrl],
                chainName: `Polygon ${networkText.replace(/\b[a-z]/g, (x) => x.toUpperCase())}`,
                nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 }
              }]
            });
          } catch (addError) {
            if (addError.code === 4001) {
              throw new Error('Please connect MetaMask to Polygon network.');
            } else {
              console.error(addError);
            }
          }
        } else if (switchError.code === 4001) {
          throw new Error('Please connect MetaMask to Polygon network.');
        } else {
          console.error(switchError);
        }
      }
    },

    // Send a batch transfer based on donation inputs
    async checkoutWithPolygon() {
      try {

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

        // If user has enough balance within Polygon, cost equals the minimum amount
        let { isBalanceSufficient, requiredAmounts } = await this.hasEnoughBalanceInPolygon();

        if (!isBalanceSufficient) {
          this.polygon.showModal = true;
          this.polygon.checkoutStatus = 'not-started';

          this.user.requiredAmounts = objectMap(requiredAmounts, value => {
            if (value.isBalanceSufficient == false) {
              return value.amount;
            }
          });
          return;
        }

        await this.setupPolygon();

        // Token approvals and balance checks from bulk checkout contract
        // (just checks data, does not execute approvals)
        const allowanceData = await this.getAllowanceData(
          ethereum.selectedAddress, bulkCheckoutAddressPolygon
        );

        // Save off cart data
        this.polygon.checkoutStatus = 'pending';

        if (allowanceData.length === 0) {
          // Send transaction and exit function
          await this.sendDonationTx(ethereum.selectedAddress);
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
      // Get our donation inputs
      const bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddressPolygon);
      const donationInputsFiltered = this.getDonationInputs();

      // Send transaction
      bulkTransaction.methods
        .donate(donationInputsFiltered)
        .send({ from: userAddress, gas: this.polygon.estimatedGasCost, value: this.donationInputsNativeAmount })
        .on('transactionHash', async(txHash) => {
          indicateMetamaskPopup(true);
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
      // The below heuristics are used instead of `estimateGas()` so we can send the donation
      // transaction before the approval txs are confirmed, because if the approval txs
      // are not confirmed then estimateGas will fail.

      return 70000;
    },

    // Returns true if user has enough balance within Polygon to avoid L1 deposit, false otherwise
    async hasEnoughBalanceInPolygon() {
      const requiredAmounts = {}; // keys are token symbols, values are required amounts as BigNumber

      // Get total amount needed for eack token by summing over donation inputs
      this.donationInputs.forEach((donation) => {
        const tokenSymbol = donation.name;
        const amount = toBigNumber(donation.amount);

        if (!requiredAmounts[tokenSymbol]) {
          // First time seeing this token, set the field and initial value
          requiredAmounts[tokenSymbol] = { amount };
        } else {
          // Increment total required amount of the token with new found value
          requiredAmounts[tokenSymbol].amount = requiredAmounts[tokenSymbol].amount.add(amount);
        }
      });

      // Compare amounts needed to balance
      const web3 = this.initWeb3();
      const userAddress = ethereum.selectedAddress;
      let isBalanceSufficient = true;

      for (let i = 0; i < this.cart.tokenList.length; i += 1) {
        const tokenSymbol = this.cart.tokenList[i];

        requiredAmounts[tokenSymbol].isBalanceSufficient = true; // initialize sufficiency result
        const tokenDetails = this.getTokenByName(tokenSymbol);

        const userMaticBalance = toBigNumber(await web3.eth.getBalance(userAddress));
        const tokenIsMatic = tokenDetails.name === 'MATIC';

        // Check user matic balance against required amount
        if (userMaticBalance.lt(requiredAmounts[tokenSymbol].amount) && tokenIsMatic) {
          requiredAmounts[tokenSymbol].isBalanceSufficient = false;
          requiredAmounts[tokenSymbol].amount = parseFloat(((
            requiredAmounts[tokenSymbol].amount - userMaticBalance
          ) / 10 ** tokenDetails.decimals).toFixed(5));
          isBalanceSufficient = false;
        }

        // Check if user has enough MATIC to cover gas costs
        const gasFeeInWei = web3.utils.toWei(
          (this.polygon.estimatedGasCost * 2).toString(), 'gwei' // using 2 gwei as gas price
        );

        if (userMaticBalance.lt(gasFeeInWei)) {
          let requiredAmount = parseFloat(Number(
            web3.utils.fromWei((gasFeeInWei - userMaticBalance).toString(), 'ether')
          ).toFixed(5));

          if (requiredAmounts['MATIC']) {
            requiredAmounts['MATIC'].amount += requiredAmount;
          } else {
            requiredAmounts['MATIC'] = {
              amount: requiredAmount,
              isBalanceSufficient: false
            };
          }
        }

        // Check user token balance against required amount
        const tokenContract = new web3.eth.Contract(token_abi, tokenDetails.addr);
        const userTokenBalance = toBigNumber(await tokenContract.methods
          .balanceOf(userAddress)
          .call({ from: userAddress }));

        if (userTokenBalance.lt(requiredAmounts[tokenSymbol].amount)) {
          requiredAmounts[tokenSymbol].isBalanceSufficient = false;
          requiredAmounts[tokenSymbol].amount = parseFloat(((
            requiredAmounts[tokenSymbol].amount - userTokenBalance
          ) / 10 ** tokenDetails.decimals).toFixed(5));
          isBalanceSufficient = false;
        }
      }

      // Return result and required amounts
      return { isBalanceSufficient, requiredAmounts };
    }
  }
});
