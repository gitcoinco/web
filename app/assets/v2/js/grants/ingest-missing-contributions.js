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

      // Validate that only one of txHash and userAddress is provided
      const { txHash, userAddress } = this.form;
      const isFormComplete = Boolean(txHash) != Boolean(userAddress);

      if (!isFormComplete) {
        // Form was not filled out
        this.$set(this.errors, 'invalidForm', 'Please enter a valid transaction hash OR a valid wallet address, but not both');
      } else {
        // Form was filled out, so validate the inputs
        isValidTxHash = txHash && txHash.length === 66 && ethers.utils.isHexString('0x');
        isValidAddress = ethers.utils.isAddress(userAddress);
        
        if (txHash && !isValidTxHash) {
          this.$set(this.errors, 'txHash', 'Please enter a valid transaction hash');
        } else if (userAddress && !isValidAddress) {
          this.$set(this.errors, 'address', 'Please enter a valid address');
        }
      }

      if (Object.keys(this.errors).length) {
        return false; // there are errors the user must correct
      }

      // Returns the values. We use an empty string to tell the backend when we're not ingesting (e.g. empty txHash
      // means we're only validating based on an address)
      return {
        txHash: isValidTxHash ? txHash : '',
        // getAddress returns checksum address required by web3py, and throws if address is invalid
        userAddress: isValidAddress ? ethers.utils.getAddress(userAddress) : ''
      };
    },

    // Wrapper around web3's getTransactionReceipt so it can be used with await
    async getTxReceipt(txHash) {
      return new Promise(function(resolve, reject) {
        web3.eth.getTransactionReceipt(txHash, (err, res) => {
          if (err) {
            return reject(err);
          }
          resolve(res);
        });
      });
    },

    async ingest(event) {
      let txHash;
      let userAddress;

      try {
        event.preventDefault();
        const formParams = this.checkForm();

        if (!formParams) {
          return; // Return if form is not valid
        }

        // Make sure wallet is connected
        const walletAddress = web3 ? (await web3.eth.getAccounts())[0] : undefined;

        if (!walletAddress) {
          throw new Error('Please connect a wallet');
        }

        // Parse out provided form inputs
        ({ txHash, userAddress } = formParams);
        
        // If user entered an address, verify that it matches the user's connected wallet address
        if (userAddress && ethers.utils.getAddress(userAddress) !== ethers.utils.getAddress(walletAddress)) {
          throw new Error('Provided wallet address does not match connected wallet address');
        }

        // If user entered an tx hash, verify that the transaction's from address matches the connected wallet address
        if (txHash) {
          const receipt = await this.getTxReceipt(txHash);

          if (!receipt) {
            throw new Error('Transaction hash not found. Are you sure this transaction was confirmed?');
          }
          if (ethers.utils.getAddress(receipt.from) !== ethers.utils.getAddress(walletAddress)) {
            throw new Error('Sender of the provided transaction does not match connected wallet address. Please contact Gitcoin and we can ingest your contributions for you');
          }
        }
      } catch (e) {
        this.handleError(e);
      }

      // If we are here, the provided form data is valid. However, someone could just POST directly to the endpoint,
      // so to workaround that we ask the user for a signature, and the backend will verify that signature
      const baseMessage = 'Sign this message as verification that you control the provided wallet address'; // base message that will be signed

      await postToDatabaseManualIngestion([txHash], userAddress, baseMessage); // this has it's own try/catch error handler
      this.resetForm();
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
