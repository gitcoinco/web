// Contract parameters
const contractAbi = [{ 'inputs': [ { 'components': [ { 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'internalType': 'address payable', 'name': 'dest', 'type': 'address' } ], 'internalType': 'struct BulkCheckout.Donation[]', 'name': '_donations', 'type': 'tuple[]' } ], 'name': 'donate', 'outputs': [], 'stateMutability': 'payable', 'type': 'function' }]; // eslint-disable-line
const contractAddress = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C';

// Grant data
let grantHeaders = [ 'Grant', 'Amount', 'Type', 'Total CLR Match Amount' ]; // cart column headers
let grantData = []; // data for grants in cart


Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      grantHeaders,
      grantData,
      currencies: [] // TODO update with Gitcoin's list of tokens]
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
          addr: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
          name: 'ETH',
          decimals: 18,
          priority: 1
        };
      }
      return tokens(network).filter(token => token.name === name)[0];
    },

    async checkout() {
      // Generate array of objects containing donation info from cart
      const donations = this.grantData.map((grant) => {
        const tokenDetails = this.getTokenByName(grant.grant_donation_currency);

        return {
          token: tokenDetails.addr,
          amount: String(grant.grant_donation_amount * 10 ** tokenDetails.decimals),
          dest: grant.grant_contract_address
        };
      });

      // First lets calculate the donations to Gitcoin
      const gitcoinFactor = 0.05;
      const gitcoinAddress = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
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
          token: tokenDetails.addr,
          amount: String(gitcoinDonations[token] * 10 ** tokenDetails.decimals),
          dest: gitcoinAddress
        });
      });

      console.log('Donations: ', donations);

      // Send the transaction
      const userAddress = (await web3.eth.getAccounts())[0];

      bulkTransaction = new web3.eth.Contract(contractAbi, contractAddress);
      bulkTransaction.methods.donate(donations).send({from: userAddress})
        .on('transactionHash', (txHash) => {
          console.log('txHash: ', txHash);
        })
        .on('confirmation', (confirmationNumber, receipt) => {
          console.log('confirmationNumber: ', confirmationNumber);
          console.log('receipt: ', receipt);
        })
        .on('receipt', (receipt) => {
          // receipt example
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

    // Populate currency list with selected tokens
    // TODO wait until `tokens` loads and we can show full list
    this.grantData.forEach(grant => {
      const token = grant.grant_donation_currency;

      if (!this.currencies.includes(token)) {
        this.currencies.push(token);
      }
    });
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