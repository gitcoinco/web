/**
 * @notice Vue component for managing cart and checkout process
 * @dev If you need to interact with the Rinkeby Dai contract (e.g. to reset allowances for
 * testing), use this one click dapp: https://oneclickdapp.com/drink-leopard/
 */

// Constants
const BN = web3.utils.BN;
const ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';
const MAX_UINT256 = '115792089237316195423570985008687907853269984665640564039457584007913129639935';
const gitcoinFactor = 0.05; // 5% of donation amount goes to Gitcoin
const gitcoinAddress = '0x00De4B13153673BCAE2616b67bf822500d325Fc3'; // Gitcoin donation address for mainnet and rinkeby

// Contract parameters
const bulkCheckoutAbi = [{ 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': false, 'internalType': 'address', 'name': 'dest', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'donor', 'type': 'address' }], 'name': 'DonationSent', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'OwnershipTransferred', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Paused', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': true, 'internalType': 'address', 'name': 'dest', 'type': 'address' }], 'name': 'TokenWithdrawn', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Unpaused', 'type': 'event' }, { 'inputs': [{ 'components': [{ 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'internalType': 'address payable', 'name': 'dest', 'type': 'address' }], 'internalType': 'struct BulkCheckout.Donation[]', 'name': '_donations', 'type': 'tuple[]' }], 'name': 'donate', 'outputs': [], 'stateMutability': 'payable', 'type': 'function' }, { 'inputs': [], 'name': 'owner', 'outputs': [{ 'internalType': 'address', 'name': '', 'type': 'address' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'pause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'paused', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'renounceOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'unpause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address payable', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawEther', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': '_tokenAddress', 'type': 'address' }, { 'internalType': 'address', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawToken', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }];
const bulkCheckoutAddress = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C';

// Grant data
let grantHeaders = [ 'Grant', 'Amount', 'Type', 'Total CLR Match Amount' ]; // cart column headers
let grantData = []; // data for grants in cart, initialized in mounted hook


Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      isLoading: undefined,
      grantHeaders,
      grantData,
      currencies: undefined
    };
  },

  computed: {
    /**
     * @notice Generates an object where keys are token names and value are the total amount
     * being donated in that token
     * @dev The addition here is based on human-readable numbers so BN is not needed
     */
    donationTotals() {
      const totals = {};

      this.grantData.forEach(grant => {
        if (!totals[grant.grant_donation_currency]) {
          // First time seeing this token, set the field and initial value
          totals[grant.grant_donation_currency] = grant.grant_donation_amount;
        } else {
          // We've seen this token, so just update the total
          totals[grant.grant_donation_currency] += grant.grant_donation_amount;
        }
      });
      return totals;
    },

    /**
     * @notice Returns a string of the form "3 DAI + 0.5 ETH + 10 USDC" which describe the
     * user's donations to grants
     */
    donationTotalsString() {
      if (!this.donationTotals) {
        return undefined;
      }

      let string = '';

      Object.keys(this.donationTotals).forEach(key => {
        // Round to 2 digits
        const amount = this.donationTotals[key];
        const formattedAmount = amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });

        if (string === '') {
          string += `${formattedAmount} ${key}`;
        } else {
          string += `+ ${formattedAmount} ${key}`;
        }
      });
      return string;
    },

    /**
     * @notice Generates an object where keys are token names and value are the total amount
     * being donated in that token to Gitcoin
     * @dev The addition here is based on human-readable numbers so BN is not needed. However,
     * we do get some floating point error
     */
    donationsToGitcoin() {
      const totals = {};

      this.grantData.forEach(grant => {
        if (!totals[grant.grant_donation_currency]) {
          // First time seeing this token, set the field and initial value
          totals[grant.grant_donation_currency] = grant.grant_donation_amount * 0.05;
        } else {
          // We've seen this token, so just update the total
          totals[grant.grant_donation_currency] += (grant.grant_donation_amount * 0.05);
        }
      });
      return totals;
    },

    /**
     * @notice Returns a string of the form "3 DAI + 0.5 ETH + 10 USDC" which describe the
     * user's donations to the Gitcoin grant
     */
    donationsToGitcoinString() {
      if (!this.donationsToGitcoin) {
        return undefined;
      }

      let string = '';

      Object.keys(this.donationsToGitcoin).forEach(key => {
        // Round to 2 digits
        const amount = this.donationsToGitcoin[key];
        const formattedAmount = amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 4
        });

        if (string === '') {
          string += `${formattedAmount} ${key}`;
        } else {
          string += `+ ${formattedAmount} ${key}`;
        }
      });
      return string;
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
     */
    toWeiString(number, decimals) {
      const wei = web3.utils.toWei(String(number));
      const base = new BN(10, 10);
      const factor = base.pow(new BN(18 - decimals, 10));

      return (new BN(wei)).div(factor).toString(10);
    },

    async checkout() {
      try {
        await window.ethereum.enable();
        const isDev = network === 'rinkeby'; // True if in development mode
        const userAddress = (await web3.eth.getAccounts())[0]; // Address of current user

        // Generate array of objects containing donation info from cart
        const donations = this.grantData.map((grant) => {
          const tokenDetails = this.getTokenByName(grant.grant_donation_currency);

          return {
            token: tokenDetails.addr,
            amount: this.toWeiString(grant.grant_donation_amount, tokenDetails.decimals),
            dest: grant.grant_admin_address,
            name: grant.grant_donation_currency
          };
        });

        // Append the Gitcoin donations
        Object.keys(this.donationsToGitcoin).forEach((token) => {
          const tokenDetails = this.getTokenByName(token);

          donations.push({
            amount: this.toWeiString(this.donationsToGitcoin[token], tokenDetails.decimals),
            token: tokenDetails.addr,
            dest: gitcoinAddress,
            name: token
          });
        });

        // Get token approvals
        const selectedTokens = Object.keys(this.donationTotals);

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
          const requiredAllowance = this.toWeiString(this.donationTotals[tokenDetails.name], tokenDetails.decimals);

          // Compare allowances and request approval if needed
          if (allowance.lt(new BN(requiredAllowance))) {
            indicateMetamaskPopup();
            const txHash = await tokenContract.methods
              .approve(bulkCheckoutAddress, MAX_UINT256)
              .send({ from: userAddress });

            console.log('Approval transaction: ', txHash);
            indicateMetamaskPopup(true);
          }
        } // end for each token being used for donations

        // Get the total ETH we need to send
        const initialValue = new BN('0');
        const ethAmountBN = donations.reduce((accumulator, currentValue) => {
          return currentValue.token === ETH_ADDRESS
            ? accumulator.add(new BN(currentValue.amount)) // ETH donation
            : accumulator.add(new BN('0')); // token donation
        }, initialValue);
        const ethAmountString = ethAmountBN.toString();

        // Configure our donation inputs
        const donationInputs = donations.map(donation => {
          delete donation.name;
          return donation;
        });

        // Estimate gas to send all of them
        // Arbitrarily choose to use a gas limit 10% higher than estimated gas
        bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddress);
        const estimatedGas = await bulkTransaction.methods
          .donate(donationInputs)
          .estimateGas({ from: userAddress, value: ethAmountString});
        const gasLimit = Math.ceil(1.1 * estimatedGas);

        // Send the transaction
        indicateMetamaskPopup();
        const txHash = await bulkTransaction.methods
          .donate(donationInputs)
          .send({ from: userAddress, gas: gasLimit, value: ethAmountString });

        console.log('Donation transaction: ', txHash);
        indicateMetamaskPopup(true);
      } catch (err) {
        this.handleError(err);
      }
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
    while (!this.currencies) {
      try {
        this.currencies = tokens(network).map(token => token.name);
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