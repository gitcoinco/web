let grantHeaders = [ 'Grant', 'Amount', 'Type', 'Total CLR Match Amount' ];
let grantData = [];

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      grantHeaders,
      grantData,
      currencies: [ 'ETH', 'DAI', 'USDC' ] // TODO update with Gitcoin's list of tokens
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