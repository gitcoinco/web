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
        txHash: undefined, // user transaction hash, used to ingest L1 donations
        userAddress: undefined // user address, used to ingest zkSync (L2) donations
      },
      errors: {}, // keys are errors that occurred
      submitted: false // true if form has been submitted and we are waiting on response
    };
  },

  methods: {
    checkForm() {
      this.submitted = true;
      this.errors = {};
      let isValidTxHash;
      let isValidAddress;

      // Validate that at least one of txHash and userAddress is provided
      const { txHash, userAddress } = this.form;
      const isFormComplete = txHash || userAddress;

      if (!isFormComplete) {
        // Form was not filled out
        this.$set(this.errors, 'invalidForm', 'Please enter a valid transaction hash or a valid wallet address');
      } else {
        // Form was filled out, so validate the inputs
        isValidTxHash = txHash && txHash.length === 66 && txHash.startsWith('0x');
        isValidAddress = ethers.utils.isAddress(userAddress);
        
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

      return {
        txHash: isValidTxHash ? txHash : '',
        // getAddress returns checksum address required by web3py, and throws if address is invalid
        userAddress: isValidAddress ? ethers.utils.getAddress(userAddress) : ''
      };
    },

    async ingest(event) {
      try {
        event.preventDefault();

        // Return if form is not valid
        const formParams = this.checkForm();

        if (!formParams) {
          return;
        }

        // Send POST requests to ingest contributions
        const { txHash, userAddress } = formParams;
        const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = '/grants/ingest';
        const headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' };
        const payload = {
          csrfmiddlewaretoken,
          txHash,
          userAddress,
          network: document.web3network || 'mainnet'
        };
        const postParams = {
          method: 'POST',
          headers,
          body: new URLSearchParams(payload)
        };

        // Send saveSubscription request
        const res = await fetch(url, postParams);
        const json = await res.json();
        
        // Notify user of success status, and clear form if successful
        console.log('ingestion response: ', json);
        if (!json.success) {
          console.log('ingestion failed');
          this.submitted = false;
          throw new Error('Your transactions could not be processed, please try again');
        } else {
          console.log('ingestion successful');
          _alert('Your contributions have been added successfully!', 'success');
          this.resetForm();
        }
      } catch (e) {
        this.handleError(e);
      }
    },

    resetForm() {
      this.form.txHash = undefined;
      this.form.userAddress = undefined;
      this.errors = {};
      this.submitted = false;
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
      this.submitted = false;
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
