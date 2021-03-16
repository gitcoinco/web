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

    // Asks user to sign a message as verification they own the provided address
    async signMessage(userAddress) {
      const baseMessage = 'Sign this message as verification that you control the provided wallet address'; // base message that will be signed
      const ethersProvider = new ethers.providers.Web3Provider(provider); // ethers provider instance
      const signer = ethersProvider.getSigner(); // ethers signers
      const { chainId } = await ethersProvider.getNetwork(); // append chain ID if not mainnet to mitigate replay attack
      const message = chainId === 1 ? baseMessage : `${baseMessage}\n\nChain ID: ${chainId}`;

      // Get signature from user
      const isValidSignature = (sig) => ethers.utils.isHexString(sig) && sig.length === 132; // used to verify signature
      let signature = await signer.signMessage(message); // prompt to user is here, uses eth_sign

      // Fallback to personal_sign if eth_sign isn't supported (e.g. for Status and other wallets)
      if (!isValidSignature(signature)) {
        signature = await ethersProvider.send(
          'personal_sign',
          [ ethers.utils.hexlify(ethers.utils.toUtf8Bytes(message)), userAddress.toLowerCase() ]
        );
      }

      // Verify signature
      if (!isValidSignature(signature)) {
        throw new Error(`Invalid signature: ${signature}`);
      }

      return { signature, message };
    },

    async ingest(event) {
      try {
        event.preventDefault();

        // Return if form is not valid
        const formParams = this.checkForm();

        if (!formParams) {
          return;
        }

        // Make sure wallet is connected
        let walletAddress;

        if (web3) {
          walletAddress = (await web3.eth.getAccounts())[0];
        }
        if (!walletAddress) {
          throw new Error('Please connect a wallet');
        }

        // TODO if user is staff, add a username field and bypass the below checks

        // Parse out provided form inputs
        const { txHash, userAddress } = formParams;
        
        // If user entered an address, verify that it matches the user's connected wallet address
        if (userAddress && ethers.utils.getAddress(userAddress) !== ethers.utils.getAddress(walletAddress)) {
          throw new Error('Provided wallet address does not match connected wallet address');
        }
        
        // If user entered an tx hash, verify that the tx's from address matches the connected wallet address
        let fromAddress;

        if (txHash) {
          const receipt = await this.getTxReceipt(txHash);

          if (!receipt) {
            throw new Error('Transaction hash not found. Are you sure this transaction was confirmed?');
          }
          fromAddress = receipt.from;

          if (ethers.utils.getAddress(fromAddress) !== ethers.utils.getAddress(walletAddress)) {
            throw new Error('Sender of the provided transaction does not match connected wallet address');
          }
        }
        
        // If we are here, the provided form data is valid. However, someone could just POST directly to the endpoint,
        // so to workaround that we ask the user for a signature, and the backend will verify that signature
        const { signature, message } = await this.signMessage(walletAddress);

        // Send POST requests to ingest contributions
        const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = '/grants/ingest';
        const headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' };
        const payload = {
          csrfmiddlewaretoken,
          txHash,
          userAddress,
          signature,
          message,
          network: document.web3network || 'mainnet'
        };
        const postParams = {
          method: 'POST',
          headers,
          body: new URLSearchParams(payload)
        };

        // Send saveSubscription request
        let json;

        try {
          const res = await fetch(url, postParams);

          json = await res.json();
        } catch (err) {
          console.error(err);
          throw new Error('Something went wrong. Please verify the form parameters and try again later');
        }
        
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
