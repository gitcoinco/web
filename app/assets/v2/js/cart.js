/**
 * @notice Vue component for managing cart and checkout process
 * @dev If you need to interact with the Rinkeby Dai contract (e.g. to reset allowances for
 * testing), use this one click dapp: https://oneclickdapp.com/drink-leopard/
 */

// Constants
const BN = web3.utils.BN;
const ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';
const MAX_UINT256 = '115792089237316195423570985008687907853269984665640564039457584007913129639935';
const gitcoinFactor = 0.05;
// const gitcoinAddress = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
const gitcoinAddress = '0x0000000000000000000000000001000000000000';

// Contract parameters
const bulkCheckoutAbi = [{ 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': false, 'internalType': 'address', 'name': 'dest', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'donor', 'type': 'address' }], 'name': 'DonationSent', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'OwnershipTransferred', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Paused', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': true, 'internalType': 'address', 'name': 'dest', 'type': 'address' }], 'name': 'TokenWithdrawn', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Unpaused', 'type': 'event' }, { 'inputs': [{ 'components': [{ 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'internalType': 'address payable', 'name': 'dest', 'type': 'address' }], 'internalType': 'struct BulkCheckout.Donation[]', 'name': '_donations', 'type': 'tuple[]' }], 'name': 'donate', 'outputs': [], 'stateMutability': 'payable', 'type': 'function' }, { 'inputs': [], 'name': 'owner', 'outputs': [{ 'internalType': 'address', 'name': '', 'type': 'address' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'pause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'paused', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'renounceOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'unpause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address payable', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawEther', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': '_tokenAddress', 'type': 'address' }, { 'internalType': 'address', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawToken', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }];
const bulkCheckoutAddress = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C';
const erc20Abi = [{ 'inputs': [{ 'internalType': 'string', 'name': 'name', 'type': 'string' }, { 'internalType': 'string', 'name': 'symbol', 'type': 'string' }], 'stateMutability': 'nonpayable', 'type': 'constructor' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'owner', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'spender', 'type': 'address' }, { 'indexed': false, 'internalType': 'uint256', 'name': 'value', 'type': 'uint256' }], 'name': 'Approval', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'from', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'to', 'type': 'address' }, { 'indexed': false, 'internalType': 'uint256', 'name': 'value', 'type': 'uint256' }], 'name': 'Transfer', 'type': 'event' }, { 'inputs': [{ 'internalType': 'address', 'name': 'owner', 'type': 'address' }, { 'internalType': 'address', 'name': 'spender', 'type': 'address' }], 'name': 'allowance', 'outputs': [{ 'internalType': 'uint256', 'name': '', 'type': 'uint256' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'spender', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }], 'name': 'approve', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'balanceOf', 'outputs': [{ 'internalType': 'uint256', 'name': '', 'type': 'uint256' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'decimals', 'outputs': [{ 'internalType': 'uint8', 'name': '', 'type': 'uint8' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'spender', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'subtractedValue', 'type': 'uint256' }], 'name': 'decreaseAllowance', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'spender', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'addedValue', 'type': 'uint256' }], 'name': 'increaseAllowance', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'account', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }], 'name': 'mint', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'name', 'outputs': [{ 'internalType': 'string', 'name': '', 'type': 'string' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'symbol', 'outputs': [{ 'internalType': 'string', 'name': '', 'type': 'string' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'totalSupply', 'outputs': [{ 'internalType': 'uint256', 'name': '', 'type': 'uint256' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'recipient', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }], 'name': 'transfer', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'sender', 'type': 'address' }, { 'internalType': 'address', 'name': 'recipient', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }], 'name': 'transferFrom', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'nonpayable', 'type': 'function' }];

// Grant data
let grantHeaders = [ 'Grant', 'Amount', 'Type', 'Total CLR Match Amount' ]; // cart column headers
let grantData = []; // data for grants in cart


Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      grantHeaders,
      grantData,
      currencies: [ 'DAI', 'ETH' ] // TODO update with Gitcoin's list of tokens]
    };
  },

  computed: {
    donationTotals() {
      const totals = {};

      this.grantData.forEach(grant => {
        const token = grant.grant_donation_currency;

        if (!totals[token]) {
          // First time seeing this token, set the field and initial value
          totals[token] = grant.grant_donation_amount;
        } else {
          // We've seen this token, so just update the total
          totals[token] += grant.grant_donation_amount;
        }
      });
      return totals;
    },

    donationTotalsString() {
      const totals = this.donationTotals;
      let string = '';

      if (!totals) {
        return undefined;
      }

      Object.keys(totals).forEach(key => {
        if (string === '') {
          string += `${totals[key]} ${key}`;
        } else {
          string += `+ ${totals[key]} ${key}`;
        }
      });
      return string;
    },

    donationsToGitcoin() {
      const totals = {};

      this.grantData.forEach(grant => {
        const token = grant.grant_donation_currency;

        if (!totals[token]) {
          // First time seeing this token, set the field and initial value
          totals[token] = grant.grant_donation_amount * 0.05;
        } else {
          // We've seen this token, so just update the total
          totals[token] += (grant.grant_donation_amount * 0.05);
        }
      });
      return totals;
    },

    donationsToGitcoinString() {
      const totals = this.donationsToGitcoin;
      let string = '';

      if (!totals) {
        return undefined;
      }

      Object.keys(totals).forEach(key => {
        // Round to 2 digits
        const amount = totals[key];
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

    async checkout() {
      // Get address of current user
      const userAddress = (await web3.eth.getAccounts())[0];

      // Generate array of objects containing donation info from cart
      const donations = this.grantData.map((grant) => {
        const tokenDetails = this.getTokenByName(grant.grant_donation_currency);

        return {
          token: tokenDetails.addr,
          amount: String(grant.grant_donation_amount * 10 ** tokenDetails.decimals),
          // dest: grant.grant_contract_address,
          dest: '0x0000000000000000000000000001000000000000',
          name: grant.grant_donation_currency
        };
      });

      // Now we calculate the additional donations to Gitcoin
      const gitcoinDonations = {};

      this.grantData.forEach((grant) => {
        const currency = grant.grant_donation_currency;
        const amount = grant.grant_donation_amount;
        const amountToGitcoin = (gitcoinFactor * amount);

        if (gitcoinDonations[currency]) {
          gitcoinDonations[currency] += amountToGitcoin;
        } else {
          gitcoinDonations[currency] = amountToGitcoin;
        }
      });

      // Append the Gitcoin donations
      Object.keys(gitcoinDonations).forEach((token) => {
        const tokenDetails = this.getTokenByName(token);

        donations.push({
          amount: String(gitcoinDonations[token] * 10 ** tokenDetails.decimals),
          token: tokenDetails.addr,
          dest: gitcoinAddress,
          name: token
        });
      });

      // Now, `donations` contains an array of all donations to make.
      // For convenience we generate a condensed version containing the totals by token
      const condensedDonations = {};

      donations.forEach(donation => {
        if (condensedDonations[donation.name]) {
          condensedDonations[donation.name] += Number(donation.amount);
        } else {
          condensedDonations[donation.name] = Number(donation.amount);
        }
      });

      // Get token approvals
      // TODO this can be more efficient by looping over condensedDonations
      const selectedTokens = Object.keys(condensedDonations);

      for (let i = 0; i < selectedTokens.length; i += 1) {
        const tokenDetails = this.getTokenByName(selectedTokens[i]);

        // If ETH donation, no approval necessary
        if (tokenDetails.name === 'ETH') {
          continue;
        }

        // Check allowance
        const tokenContract = new web3.eth.Contract(erc20Abi, tokenDetails.addr);
        const allowance = new BN(
          await tokenContract.methods
            .allowance(userAddress, bulkCheckoutAddress)
            .call({ from: userAddress })
        );

        // Check allowance against the total being donated of that token
        const requiredAllowance = new BN(String(condensedDonations[tokenDetails.name]));

        if (allowance.lt(requiredAllowance)) {
          // Allowance is too small, ask for approval
          indicateMetamaskPopup();
          const txHash = await tokenContract.methods.approve(bulkCheckoutAddress, MAX_UINT256).send({ from: userAddress });

          indicateMetamaskPopup(true);
        }
      } // end for each donation

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
      bulkTransaction.methods
        .donate(donationInputs)
        .send({ from: userAddress, gas: gasLimit, value: ethAmountString })
        .on('transactionHash', (txHash) => {
          indicateMetamaskPopup(true);
          console.log('txHash: ', txHash);
        })
        .on('receipt', (receipt) => {
          console.log(receipt);
        })
        .on('error', (err) => {
          console.error(err);
        });
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

  mounted() {
    // Read array of grants in cart from localStorage
    this.grantData = JSON.parse(window.localStorage.getItem('grants_cart'));

    // // Populate currency list with selected tokens
    // // TODO wait until `tokens` loads and we can show full list
    // this.grantData.forEach(grant => {
    //   const token = grant.grant_donation_currency;

    //   if (!this.currencies.includes(token)) {
    //     this.currencies.push(token);
    //   }
    // });
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