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
    grantsByTenant: { type: Array, required: true }, // Array of grants in cart
    maxCartItems: { type: Number, required: true }, // max number of items in cart
    network: { type: String, required: true }, // web3 network to use
    grantsUnderMinimalContribution: { type: Array, required: true } // Array of grants under min contribution
  },

  data: function() {
    return {
      ethersProvider: undefined,

      zksync: {
        checkoutManager: undefined, // zkSync API CheckoutManager class
        feeTokenSymbol: undefined, // token symbol to pay zksync fee with, e.g. 'DAI'
        showChangeToken: false, // true to show dropdown to let user select feeTokenSymbol
        showModal: false, // true to show modal to user, false to hide
        checkoutStatus: 'not-started', // options are 'not-started', 'pending', and 'complete'
        contractAddress: '0xaBEA9132b05A70803a4E85094fD0e1800777fBEF' // mainnet contract address
      },

      cart: {
        tokenList: [], // array of tokens in the cart
        unsupportedTokens: [] // tokens in cart which are not supported by zkSync
      },

      user: {
        address: undefined, // connected web3 wallet address
        zkSyncState: undefined, // contains account balances of zkSync wallet
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
      if (this.zksync.checkoutStatus === 'pending') {
        e.returnValue = 'zkSync checkout in progress. Are you sure you want to leave?';
      }
    });

    // Update zkSync checkout connection, state, and data frontend needs when wallet connection changes
    window.addEventListener('dataWalletReady', async(e) => {
      await this.setupZkSync();
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
    },

    // Array of transfer objects in the format zkSync needs
    transfers() {
      // Generate array of objects used to send the transfer. We give each transfer a fee of zero,
      // then zkSync will append one more zero-value transfer that covers the full fee
      return this.donationInputs.map((donation) => {
        return {
          from: this.user.address, // if user connects to zkSync with a different address, it will notify them
          to: getAddress(donation.dest), // ensure we use a checksummed address
          token: donation.name, // token symbol
          amount: donation.amount,
          description: donation.grant.grant_title,
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
        // Update state and data that frontend needs
        await this.onChangeHandler(donations);
      }
    },

    // When network changes we need to update zkSync config, fetch new balances, etc.
    network: {
      immediate: true,
      async handler() {
        await this.setupZkSync();
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

      if (this.cart.unsupportedTokens.length > 0) {
        _alert(`zkSync checkout not supported due to the use of the token ${this.cart.unsupportedTokens[0]}`, 'danger');
      }

      // If currently selected fee token is still in the cart, don't change it. Otherwise, set
      // fee token to the token used for the first item in the cart
      if (!this.cart.tokenList.includes(this.zksync.feeTokenSymbol)) {
        this.zksync.feeTokenSymbol = donations[0].name;
      }

      // If no checkoutManager instance, return, since we can't check balance or estimate gas cost
      if (!this.zksync.checkoutManager) {
        return;
      }

      // Check if user has enough balance
      this.zksync.checkoutManager
        .checkEnoughBalance(this.transfers, this.zksync.feeTokenSymbol, this.user.address, this.ethersProvider)
        .then((hasEnoughBalance) => {
          this.user.hasEnoughBalance = hasEnoughBalance;
          // If they have insufficient balance but modal is already visible, alert user.
          // This happens if the balance check promise resolves after the user opens the modal
          if (!this.user.hasEnoughBalance && this.zksync.showModal)
            this.insufficientBalanceAlert();
        })
        .catch((e) => {
          // Assume user has enough balance if there's an error
          console.warn(e);
          this.user.hasEnoughBalance = true;
        });

      // Update the fee estimate and gas cost based on changes
      const estimatedGasCost = this.estimateGasCost();

      // Emit event so cart.js can update state accordingly to display info to user
      this.$emit('zksync-data-updated', {
        zkSyncEstimatedGasCost: estimatedGasCost
      });
    },

    // Alert user they have insufficient balance to complete checkout
    insufficientBalanceAlert() {
      this.zksync.showModal = false; // hide checkout modal if visible
      this.resetZkSyncModal(); // reset modal settings

      this.handleError(new Error('There is an insufficient balance to complete checkout. Please load funds and try again.')); // throw error and show to user
    },

    // Reset zkSync modal status after a checkout failure
    resetZkSyncModal() {
      this.zksync.checkoutStatus = 'not-started';
    },

    // Called on page load to initialize zkSync
    async setupZkSync() {
      const network = (this.network === 'testnet' ? 'rinkeby' : this.network) || 'mainnet'; // fallback to mainnet if no wallet is connected

      if (!web3Modal || !provider) {
        return; // exit if web3 isn't defined, and we'll run this function later
      }

      this.user.address = (await web3.eth.getAccounts())[0];
      this.ethersProvider = ethers.getDefaultProvider(network, {
        infura: document.contxt.INFURA_V3_PROJECT_ID
        // etherscan: YOUR_ETHERSCAN_API_KEY,
        // alchemy: YOUR_ALCHEMY_API_KEY,
        // pocket: YOUR_POCKET_APPLICATION_KEY
      });

      this.zksync.checkoutManager = new ZkSyncCheckout.CheckoutManager(network);
      this.user.zksyncState = await this.zksync.checkoutManager.getState(this.user.address);
    },

    // Send a batch transfer based on donation inputs
    async checkoutWithZksync() {
      try {
        // Ensure wallet is connected
        if (!web3) {
          throw new Error('Please connect a wallet');
        }

        let networkId = String(Number(web3.eth.currentProvider.chainId));

        if (networkId !== '1' && networkId !== '4') {
          // User MetaMask must be connected to Ethereum mainnet
          try {
            await ethereum.request({
              method: 'wallet_switchEthereumChain',
              params: [{ chainId: '0x1' }]
            });
          } catch (switchError) {
            if (switchError.code === 4001) {
              throw new Error('Please connect MetaMask to Ethereum network.');
            } else if (switchError.code === -32002) {
              throw new Error('Please respond to a pending MetaMask request.');
            } else {
              console.error(switchError);
            }
          }
        }

        // Make sure setup is completed properly
        const isCorrectNetwork = this.zksync.checkoutManager && this.zksync.checkoutManager.network === this.network;

        if (!isCorrectNetwork || !this.user.address) {
          await this.setupZkSync();
        }

        // Save off cart data
        this.zksync.checkoutStatus = 'pending';

        // Send user to zkSync to complete checkout
        const txHashes = await this.zksync.checkoutManager.zkSyncBatchCheckout(
          this.transfers,
          this.zksync.feeTokenSymbol
        );

        // Save contributors to database and redirect to success modal
        console.log('zkSync transaction hashes: ', txHashes);
        _alert('Saving contributions. Please do not leave this page.', 'success', 2000);
        await appCart.$refs.cart.postToDatabase(
          txHashes, // array of transaction hashes for each contribution
          this.zksync.contractAddress, // we use the zkSync mainnet contract address to represent zkSync deposits
          this.user.address,
          'eth_zksync'
        );
        this.zksync.checkoutStatus = 'complete'; // allows user to freely close tab now
        await appCart.$refs.cart.finalizeCheckout(); // Update UI and redirect

      } catch (e) {
        switch (e) {
          case 'User closed zkSync':
            _alert('Looks like the window has been closed. To complete zkSync checkout, please try again.', 'danger');
            this.resetZkSyncModal();
            throw e;

          case 'Failed to open zkSync page':
            _alert('Opening the window took longer than expected. Checkout is not complete: Unable to open the zkSync page. Please try again', 'danger');
            this.resetZkSyncModal();
            throw e;

          case 'Took too long for the zkSync page to open':
            _alert('The browser failed to open zkSync. Checkout is not complete. Please try again', 'danger');
            this.resetZkSyncModal();
            throw e;

          default:
            this.handleError(e);
        }
      }
    },

    // Estimates the total gas cost of a zkSync checkout and sends it to cart.js
    estimateGasCost() {
      if (!this.user.zksyncState)
        return;

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
