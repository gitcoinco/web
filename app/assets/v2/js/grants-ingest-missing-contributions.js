/**
 * @notice Vue component for ingesting contributions that were missed during checkout
 * @dev See more at: https://github.com/gitcoinco/web/issues/7744
 */

let appIngestContributions;

Vue.component('grants-ingest-contributions', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      form: {
        txHash: undefined,
        userAddress: undefined
      },
      errors: {},
      submitted: false
    };
  },

  methods: {
    checkForm() {
      this.submitted = true;
      this.errors = {};

      // Validate that at least one of txHash and userAddress is provided
      const { txHash, userAddress } = this.form;
      const isFormComplete = txHash || userAddress;

      if (!isFormComplete) {
        this.$set(this.errors, 'invalidForm', 'Please enter a valid transaction hash or a valid wallet address');
      } else {
        const isValidTxHash = txHash && txHash.length === 66 && txHash.startsWith('0x');
        const isValidAddress = ethers.utils.isAddress(userAddress);
        
        if (txHash && !isValidTxHash) {
          this.$set(this.errors, 'txHash', 'Please enter a valid transaction hash');
        }
        if (userAddress && !isValidAddress) {
          this.$set(this.errors, 'address', 'Please enter a valid address');
        }
      }

      if (Object.keys(this.errors).length) {
        return false; // there are errors the user must correct
      }

      this.submitted = false;
    },

    async ingest(event) {
      event.preventDefault();
      console.log('ingesting...');

      // Exit if form is not valid
      if (!this.checkForm()) {
        return;
      }
    }
  },

  watch: {
    deep: true,
    form: {
      deep: true,
      handler(newVal, oldVal) {
        this.checkForm();
        this.submitted = false;
        this.errors = {};
      }
    }
  }
});

if (document.getElementById('gc-grants-ingest-contributions')) {

  appIngestContributions = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-ingest-contributions'
  });
}
