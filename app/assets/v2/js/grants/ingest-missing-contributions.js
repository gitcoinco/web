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
        chain: undefined,
        checkoutType: undefined,
        txHash: undefined, // user transaction hash, used to ingest L1 and Polygon L2 donations
        userAddress: undefined, // user address, used to ingest zkSync (L2) donations
        handle: undefined // user to ingest under -- ignored unless you are a staff
      },
      checkoutOptions: [
        { value: 'eth_std', label: 'Standard' },
        { value: 'eth_zksync', label: 'zkSync' },
        { value: 'eth_polygon', label: 'Polygon'}
      ],
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

      // Validate that only one of txHash and userAddress is provided. We only allow one because (1) that will be the
      // most common use case, and (2) later when we update cart.js to fallback to manual ingestion if regular POSTing
      // fails, that will make DRYing the manual ingestion code simpler. Reference implementation of DRY code for
      // fallback to manual ingestion here: https://github.com/gitcoinco/web/pull/8563
      const { checkoutType, txHash, userAddress } = this.form;

      // Form was filled out, so validate the inputs
      isValidTxHash = txHash && txHash.length === 66 && ethers.utils.isHexString(txHash);
      isValidAddress = ethers.utils.isAddress(userAddress);

      if (!checkoutType) {
        this.$set(this.errors, 'checkoutType', 'Please select a valid checkout type');
      }
      
      if ((!txHash || !isValidTxHash) && (checkoutType == 'eth_std' || checkoutType == 'eth_polygon')) {
        this.$set(this.errors, 'txHash', 'Please enter a valid transaction hash');
      }

      if ((!userAddress || !isValidAddress) && (checkoutType == 'eth_zksync')) {
        this.$set(this.errors, 'address', 'Please enter a valid address');
      }

      if (document.contxt.is_staff && !this.form.handle) {
        this.$set(this.errors, 'handle', 'Since you are staff, you must enter the handle of the profile to ingest for');
      }

      if (Object.keys(this.errors).length) {
        return false; // there are errors the user must correct
      }

      // Returns the values. We use an empty string to tell the backend when we're not ingesting (e.g. empty txHash
      // means we're only validating based on an address)
      return {
        txHash: isValidTxHash ? txHash : '',
        // getAddress returns checksum address required by web3py, and throws if address is invalid
        userAddress: isValidAddress ? ethers.utils.getAddress(userAddress) : '',
        checkoutType: checkoutType
      };
    },

    // Wrapper around web3's getTransactionReceipt so it can be used with await
    async getTxReceipt(txHash) {
      return new Promise(function(resolve, reject) {
        web3.eth.getTransactionReceipt(txHash, (err, res) => {
          if (err) {
            console.log({ err });
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
        console.error('Invalid signature', signature);
        throw new Error('Invalid signature. Please try again');
      }

      return { signature, message };
    },

    async ingest(event) {
      let txHash;
      let userAddress;

      try {
        event.preventDefault();
        const formParams = this.checkForm();

        if (!formParams) {
          return; // return if form is not valid
        }

        // Make sure wallet is connected
        let walletAddress = selectedAccount;

        if (!walletAddress) {
          initWallet();
          await onConnect();
          walletAddress = selectedAccount;
        }

        if (!walletAddress) {
          throw new Error('Please connect a wallet');
        }
        
        if (!window.ethereum) {
          throw new Error('Metamask is either not installed or blocked by a third party');
        }

        // Parse out provided form inputs and verify them, but bypass address checks if user is staff
        ({ txHash, userAddress, checkoutType } = formParams);
        
        if (checkoutType === 'eth_polygon') {
          await setupPolygon('mainnet'); // handles switching to polygon network + adding network config if doesn't exist
        }

        // If user entered an address, verify that it matches the user's connected wallet address
        if (!document.contxt.is_staff && userAddress && ethers.utils.getAddress(userAddress) !== ethers.utils.getAddress(walletAddress)) {
          throw new Error('Provided wallet address does not match connected wallet address');
        }

        // If user entered an tx hash, verify that the tx's from address matches the connected wallet address
        if (txHash) {
          const receipt = await this.getTxReceipt(txHash);

          if (!receipt) {
            throw new Error("Transaction hash not found. Are you sure this transaction was confirmed and you're on the right network?");
          }
          if (!document.contxt.is_staff && ethers.utils.getAddress(receipt.from) !== ethers.utils.getAddress(walletAddress)) {
            throw new Error('Sender of the provided transaction does not match connected wallet address. Please contact Gitcoin and we can ingest your contributions for you');
          }
        }

        // If we are here, the provided form data is valid. However, someone could just POST directly to the endpoint,
        // so to workaround that we ask the user for a signature, and the backend will verify that signature
        const { signature, message } = await this.signMessage(walletAddress);

        let chain = undefined;

        if (checkoutType == 'eth_polygon') {
          chain = 'polygon';
        } else {
          chain = 'std';
        }

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
          network: document.web3network || 'mainnet',
          handle: this.form.handle,
          chain: chain
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
          const msg = json.message ?
            'Error adding contributions as ' + json.message :
            'Error adding contributions, please try again';

          throw new Error(msg);
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

      _alert(message, 'danger');
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
