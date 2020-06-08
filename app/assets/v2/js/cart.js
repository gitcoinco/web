/**
 * @notice Vue component for managing cart and checkout process
 * @dev If you need to interact with the Rinkeby Dai contract (e.g. to reset allowances for
 * testing), use this one click dapp: https://oneclickdapp.com/drink-leopard/
 */

// Constants
const BN = web3.utils.BN;
const ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';
const gitcoinAddress = '0x00De4B13153673BCAE2616b67bf822500d325Fc3'; // Gitcoin donation address for mainnet and rinkeby

// Contract parameters
const bulkCheckoutAbi = [{ 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': false, 'internalType': 'address', 'name': 'dest', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'donor', 'type': 'address' }], 'name': 'DonationSent', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'OwnershipTransferred', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Paused', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': true, 'internalType': 'address', 'name': 'dest', 'type': 'address' }], 'name': 'TokenWithdrawn', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Unpaused', 'type': 'event' }, { 'inputs': [{ 'components': [{ 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'internalType': 'address payable', 'name': 'dest', 'type': 'address' }], 'internalType': 'struct BulkCheckout.Donation[]', 'name': '_donations', 'type': 'tuple[]' }], 'name': 'donate', 'outputs': [], 'stateMutability': 'payable', 'type': 'function' }, { 'inputs': [], 'name': 'owner', 'outputs': [{ 'internalType': 'address', 'name': '', 'type': 'address' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'pause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'paused', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'renounceOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'unpause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address payable', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawEther', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': '_tokenAddress', 'type': 'address' }, { 'internalType': 'address', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawToken', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }];
const bulkCheckoutAddress = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C';

// Grant data
let grantHeaders = [ 'Grant', 'Amount', 'Total CLR Match Amount' ]; // cart column headers
let grantData = []; // data for grants in cart, initialized in mounted hook


Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      adjustGitcoinFactor: false, // if true, show section for user to adjust Gitcoin's percentage
      tokenList: undefined, // array of all tokens for selected network
      isLoading: undefined,
      gitcoinFactorRaw: 5, // By default, 5% of donation amount goes to Gitcoin
      grantHeaders,
      grantData
    };
  },

  computed: {
    // Array of arrays, item i lists supported tokens for donating to grant given by grantData[i]
    currencies() {
      if (!this.grantData || !this.tokenList)
        return undefined;

      // Get supported tokens for each grant
      const currencies = this.grantData.map(grant => {
        // Return full list if grant accepts all tokens
        if (grant.grant_token_address === '0x0000000000000000000000000000000000000000') {
          return this.tokenList.map(token => token.name);
        }

        // Return ETH + selected token otherwise
        let allowedTokens = ['ETH'];

        this.tokenList.forEach(tokenData => {
          if (tokenData.addr === grant.grant_token_address)
            allowedTokens.push(tokenData.name);
        });
        return allowedTokens;
      });

      return currencies;
    },

    // Percentage of donation that goes to Gitcoin
    gitcoinFactor() {
      return this.gitcoinFactorRaw / 100;
    },

    // Amounts being donated to grants
    donationsToGrants() {
      return this.donationSummaryTotals(1 - this.gitcoinFactor);
    },

    // Amounts being donated to Gitcoin
    donationsToGitcoin() {
      return this.donationSummaryTotals(this.gitcoinFactor);
    },

    // Total amounts being donated
    donationsTotal() {
      return this.donationSummaryTotals(1);
    },

    // String describing user's donations to grants
    donationsToGrantsString() {
      return this.donationSummaryString('donationsToGrants', 2);
    },

    // String describing user's donations to Gitcoin
    donationsToGitcoinString() {
      return this.donationSummaryString('donationsToGitcoin', 4);
    },

    // String describing user's total donations
    donationsTotalString() {
      return this.donationSummaryString('donationsTotal', 2);
    },

    // Array of objects containing all donations and associated data
    donationInputs() {
      if (!this.grantData)
        return undefined;

      // Generate array of objects containing donation info from cart
      let gitcoinFactor = 100 * this.gitcoinFactor;
      const donations = this.grantData.map((grant) => {
        const tokenDetails = this.getTokenByName(grant.grant_donation_currency);
        const amount = this.toWeiString(grant.grant_donation_amount, tokenDetails.decimals, 100 - gitcoinFactor);

        return {
          token: tokenDetails.addr,
          amount,
          dest: grant.grant_admin_address,
          name: grant.grant_donation_currency
        };
      });

      // Append the Gitcoin donations (these already account for gitcoinFactor)
      Object.keys(this.donationsToGitcoin).forEach((token) => {
        const tokenDetails = this.getTokenByName(token);
        const amount = this.toWeiString(this.donationsToGitcoin[token], tokenDetails.decimals);

        donations.push({
          amount,
          token: tokenDetails.addr,
          dest: gitcoinAddress,
          name: token
        });
      });
      return donations;
    },

    // Amount of ETH that needs to be sent along with the transaction
    donationInputsEthAmount() {
      // Get the total ETH we need to send
      const initialValue = new BN('0');
      const ethAmountBN = this.donationInputs.reduce((accumulator, currentValue) => {
        return currentValue.token === ETH_ADDRESS
          ? accumulator.add(new BN(currentValue.amount)) // ETH donation
          : accumulator.add(new BN('0')); // token donation
      }, initialValue);

      return ethAmountBN.toString(10);
    },

    // Estimated gas limit for the transaction
    donationInputsGasLimit() {
      // Based on contract tests, we use the heuristic below to get gas estimate. This is done
      // instead of `estimateGas()` so we can send the donation transaction before the approval txs
      // are confirmed, because if the approval txs are not confirmed then estimateGas will fail.
      // The estimates used here are based on single donations (i.e. one item in the cart). Because
      // gas prices go down with batched transactions, whereas this assumes they're constant,
      // this gives us a conservative estimate
      const gasLimit = this.donationInputs.reduce((accumulator, currentValue) => {
        return currentValue.token === ETH_ADDRESS
          ? accumulator + 50000// ETH donation gas estimate
          : accumulator + 100000; // token donation gas estimate
      }, 0);

      return gasLimit;
    },

    maxPossibleTransactions() {
      if (!this.donationsTotal) {
        return '-';
      }

      let number = 1;

      Object.keys(this.donationsTotal).forEach((token) => {
        if (token !== 'ETH') {
          number += 1;
        }
      });
      return number;
    }
  },

  methods: {
    clearCart() {
      window.localStorage.setItem('grants_cart', JSON.stringify([]));
      this.grantData = [];
    },

    removeGrantFromCart(id) {
      this.grantData = this.grantData.filter(grant => grant.grant_id !== id);
      window.localStorage.setItem('grants_cart', JSON.stringify(this.grantData));
    },

    /**
     * @notice Generates an object where keys are token names and value are the total amount
     * being donated in that token. Scale factor scales the amounts used by a constant
     * @dev The addition here is based on human-readable numbers so BN is not needed
     */
    donationSummaryTotals(scaleFactor = 1) {
      const totals = {};

      this.grantData.forEach(grant => {
        if (!totals[grant.grant_donation_currency]) {
          // First time seeing this token, set the field and initial value
          totals[grant.grant_donation_currency] = grant.grant_donation_amount * scaleFactor;
        } else {
          // We've seen this token, so just update the total
          totals[grant.grant_donation_currency] += (grant.grant_donation_amount * scaleFactor);
        }
      });
      return totals;
    },

    /**
     * @notice Returns a string of the form "3 DAI + 0.5 ETH + 10 USDC" which describe the
     * user's donations for a given property
     */
    donationSummaryString(propertyName, maximumFractionDigits = 2) {
      if (!this[propertyName]) {
        return undefined;
      }

      let string = '';

      Object.keys(this[propertyName]).forEach(key => {
        // Round to 2 digits
        const amount = this[propertyName][key];
        const formattedAmount = amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits
        });

        if (string === '') {
          string += `${formattedAmount} ${key}`;
        } else {
          string += `+ ${formattedAmount} ${key}`;
        }
      });
      return string;
    },

    handleError(err) {
      console.error(err); // eslint-disable-line no-console
      let message = 'There was an error';

      if (err.message)
        message = err.message;
      else if (err.msg)
        message = err.msg;
      else if (typeof err === 'string')
        message = err;

      _alert(message, 'error');
      indicateMetamaskPopup(true);
    },

    /**
     * @notice Get token address and decimals
     * @dev We use this instead of tokenNameToDetails in tokens.js because we use a different
     * address to represent ETH
     * @param {String} name Token name, e.g. ETH or DAI
     */
    getTokenByName(name) {
      if (name === 'ETH') {
        return {
          addr: ETH_ADDRESS,
          name: 'ETH',
          decimals: 18,
          priority: 1
        };
      }
      return tokens(network).filter(token => token.name === name)[0];
    },

    /**
     * @notice Returns a string of the human-readable value, in "Wei", where by wei we refer
     * to the proper integer value based on the number of token decimals
     * @param {Number} number Human-readable number to convert, e.g. 0.1 or 3
     * @param {Number} decimals Number of decimals for conversion to Wei
     * @param {Number} scaleFactor Factor to multiply number by, as percent*100, e.g. value of 100
     * means multiply by scale factor of 1
     */
    toWeiString(number, decimals, scaleFactor = 100) {
      const wei = web3.utils.toWei(String(number));
      const base = new BN(10, 10);
      const factor = base.pow(new BN(18 - decimals, 10));
      const scale = new BN(scaleFactor, 10);
      const amount = (new BN(wei)).mul(scale).div(new BN(100, 10));

      return amount.div(factor).toString(10);
    },

    /**
     * @notice Checkout flow
     */
    async checkout() {
      try {
        // Setup -----------------------------------------------------------------------------------
        await window.ethereum.enable();
        const userAddress = (await web3.eth.getAccounts())[0]; // Address of current user

        // Get list of tokens user is donating with
        const selectedTokens = Object.keys(this.donationsToGrants);

        // Token approval checks -------------------------------------------------------------------
        // For each token, check if an approval is needed, and if so save off the data
        let allowanceData = [];

        for (let i = 0; i < selectedTokens.length; i += 1) {
          const tokenDetails = this.getTokenByName(selectedTokens[i]);

          // If ETH donation, no approval necessary
          if (tokenDetails.name === 'ETH') {
            continue;
          }

          // Get current allowance
          const tokenContract = new web3.eth.Contract(token_abi, tokenDetails.addr);
          const allowance = new BN(
            await tokenContract.methods
              .allowance(userAddress, bulkCheckoutAddress)
              .call({ from: userAddress })
          );

          // Get required allowance based on donation amounts
          // We use reduce instead of this.donationsTotal because this.donationsTotal will
          // not have floating point errors, but the actual amounts used will
          const initialValue = new BN('0');
          const requiredAllowance = this.donationInputs.reduce((accumulator, currentValue) => {
            return currentValue.token === tokenDetails.addr
              ? accumulator.add(new BN(currentValue.amount)) // correct token donation
              : accumulator.add(new BN('0')); // ETH donation
          }, initialValue);

          // If no allowance is needed, continue to next token
          if (allowance.gte(new BN(requiredAllowance))) {
            continue;
          }

          // If we do need to set the allowance, save off the required info
          allowanceData.push({
            allowance: requiredAllowance.toString(),
            contract: tokenContract
          });
        } // end checking approval requirements for each token being used for donations

        // Send donation if no approvals -----------------------------------------------------------
        if (allowanceData.length === 0) {
          // Send transaction and exit function
          this.sendDonationTx(userAddress);
          return;
        }

        // Get approvals then send donation --------------------------------------------------------
        indicateMetamaskPopup();
        for (let i = 0; i < allowanceData.length; i += 1) {
          const allowance = allowanceData[i].allowance;
          const contract = allowanceData[i].contract;
          const approvalTx = contract.methods.approve(bulkCheckoutAddress, allowance);

          // We split this into two very similar branches, because on the last approval
          // we send the main donation transaction after we get the transaction hash
          if (i !== allowanceData.length - 1) {
            approvalTx.send({ from: userAddress })
              .on('error', (error, receipt) => {
                // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
                this.handleError(error);
              });
          } else {
            approvalTx.send({ from: userAddress })
              .on('transactionHash', (txHash) => { // eslint-disable-line no-loop-func
                indicateMetamaskPopup(true);
                this.sendDonationTx(userAddress);
              })
              .on('error', (error, receipt) => {
                // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
                this.handleError(error);
              });
          }
        }
      } catch (err) {
        this.handleError(err);
      }
    },

    sendDonationTx(userAddress) {
      // Configure our donation inputs
      const bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddress);
      const donationInputs = this.donationInputs.map(donation => {
        delete donation.name;
        return donation;
      });

      indicateMetamaskPopup();
      bulkTransaction.methods
        .donate(donationInputs)
        .send({ from: userAddress, gas: this.donationInputsGasLimit, value: this.donationInputsEthAmount })
        .on('transactionHash', (txHash) => {
          console.log('Donation transaction: ', txHash);
          indicateMetamaskPopup(true);
        })
        .on('confirmation', (confirmationNumber, receipt) => {
          // TODO?
        })
        .on('error', (error, receipt) => {
          // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
          this.handleError(error);
        });
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  },

  watch: {
    // Use watcher to keep local storage in sync with Vue state
    grantData: {
      handler() {
        window.localStorage.setItem('grants_cart', JSON.stringify(this.grantData));
      },
      deep: true
    }
  },

  async mounted() {
    // Show loading dialog
    this.isLoading = true;
    // Read array of grants in cart from localStorage
    this.grantData = JSON.parse(window.localStorage.getItem('grants_cart'));
    // Wait until we can load token list
    while (!this.tokenList) {
      try {
        this.tokenList = tokens(network);
      } catch (err) {}
      await this.sleep(50); // every 50 ms
    }
    // Cart is now ready
    this.isLoading = false;
  }
});

if (document.getElementById('gc-grants-cart')) {

  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-cart',
    data: {
      grantHeaders,
      grantData
    }
  });
}