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

Vue.use(VueTelInput);

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      adjustGitcoinFactor: false, // if true, show section for user to adjust Gitcoin's percentage
      tokenList: undefined, // array of all tokens for selected network
      isLoading: undefined,
      gitcoinFactorRaw: 5, // By default, 5% of donation amount goes to Gitcoin
      grantHeaders,
      grantData,
      comments: undefined,
      hideWalletAddress: true,
      windowWidth: window.innerWidth,
      // SMS validation
      csrf: $("input[name='csrfmiddlewaretoken']").val(),
      validationStep: 'intro',
      showValidation: false,
      phone: '',
      validNumber: false,
      errorMessage: '',
      verified: document.verified,
      code: '',
      timePassed: 0,
      timeInterval: 0,
      display_email_option: false,
      countDownActive: false
    };
  },

  computed: {
    // Returns true if user is logged in with GitHub, false otherwise
    isLoggedIn() {
      return document.contxt.github_handle;
    },

    // Returns true of screen size is smaller than 576 pixels (Bootstrap's small size)
    isMobileDevice() {
      return this.windowWidth < 576;
    },

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
      return Number(this.gitcoinFactorRaw) / 100;
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
      const donations = this.grantData.map((grant, index) => {
        const tokenDetails = this.getTokenByName(grant.grant_donation_currency);
        const amount = this.toWeiString(
          Number(grant.grant_donation_amount),
          tokenDetails.decimals,
          100 - gitcoinFactor
        );

        return {
          token: tokenDetails.addr,
          amount,
          dest: grant.grant_admin_address,
          name: grant.grant_donation_currency, // token abbreviation, e.g. DAI
          grant, // all grant data from localStorage
          comment: this.comments[index], // comment left by donor to grant owner
          tokenApprovalTxHash: '' // tx hash of token approval required for this donation
        };
      });

      // Append the Gitcoin donations (these already account for gitcoinFactor)
      Object.keys(this.donationsToGitcoin).forEach((token) => {
        const tokenDetails = this.getTokenByName(token);
        const amount = this.toWeiString(this.donationsToGitcoin[token], tokenDetails.decimals);

        const gitcoinGrantInfo = {
          // Manually fill this in so we can access it for the POST requests.
          // We use empty strings for fields that are not needed here
          grant_admin_address: gitcoinAddress,
          grant_contract_address: '0xeb00a9c1Aa8C8f4b20C5d3dDA2bbC64Aa39AF752',
          grant_contract_version: '1',
          grant_donation_amount: this.donationsToGitcoin[token],
          grant_donation_clr_match: '',
          grant_donation_currency: token,
          grant_donation_num_rounds: 1,
          grant_id: '86',
          grant_image_css: '',
          grant_logo: '',
          grant_slug: 'gitcoin-sustainability-fund',
          grant_title: 'Gitcoin Grants Round 6+ Development Fund',
          grant_token_address: '0x0000000000000000000000000000000000000000',
          grant_token_symbol: '',
          isAutomatic: true // we add this field to help properly format the POST requests
        };

        donations.push({
          amount,
          token: tokenDetails.addr,
          dest: gitcoinAddress,
          name: token, // token abbreviation, e.g. DAI
          grant: gitcoinGrantInfo, // equivalent to grant data from localStorage
          comment: '', // comment left by donor to grant owner
          tokenApprovalTxHash: '' // tx hash of token approval required for this donation
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
    dismissVerification() {
      localStorage.setItem('dismiss-sms-validation', true);
      this.showValidation = false;
    },
    showSMSValidationModal() {
      if (!this.verified) {
        this.showValidation = true;
      } else {
        _alert('You have been verified previously');
      }
    },
    validateCode() {
      const vm = this;

      if (vm.code) {
        const verificationRequest = fetchData('/sms/validate/', 'POST', {
          code: vm.code,
          phone: vm.phone
        }, {'X-CSRFToken': vm.csrf});

        $.when(verificationRequest).then(response => {
          vm.verificationEnabled = false;
          vm.verified = true;
          vm.validationStep = 'verifyNumber';
          vm.showValidation = false;
          _alert('You have been verified', 'success');
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    startVerification() {
      this.phone = '';
      this.validationStep = 'requestVerification';
      this.validNumber = false;
      this.errorMessage = '';
      this.code = '';
      this.timePassed = 0;
      this.timeInterval = 0;
      this.display_email_option = false;
    },
    countdown() {
      const vm = this;

      if (!vm.countDownActive) {
        vm.countDownActive = true;

        setInterval(() => {
          vm.timePassed += 1;
        }, 1000);
      }
    },
    resendCode(delivery_method) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      vm.errorMessage = '';

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164,
          delivery_method: delivery_method || 'sms'
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          // set the cooldown time to one minute
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    requestVerification(event) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          vm.validationStep = 'verifyNumber';
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    isValidNumber(validation) {
      console.log(validation);
      this.validNumber = validation.isValid;
    },
    loginWithGitHub() {
      window.location.href = `${window.location.origin}/login/github/?next=/grants/cart`;
    },

    confirmClearCart() {
      if (confirm('are you sure')) {
        this.clearCart();
      }
    },

    clearCart() {
      CartData.clearCart();
      this.grantData = [];
      update_cart_title();
    },
    shareCart() {
      _alert('Cart URL copied to clipboard', 'success', 1000);
      copyToClipboard(CartData.share_url());
    },

    removeGrantFromCart(id) {
      CartData.removeIdFromCart(id);
      this.grantData = CartData.loadCart();
      update_cart_title();
    },

    addComment(id, text) {
      // Set comment at this index to an empty string to show textarea
      this.grantData[id].grant_comments = text ? text : '';
      CartData.setCart(this.grantData);
      this.$forceUpdate();

      $('input[type=textarea]').focus();
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
          totals[grant.grant_donation_currency] = Number(grant.grant_donation_amount) * scaleFactor;
        } else {
          // We've seen this token, so just update the total
          totals[grant.grant_donation_currency] += (Number(grant.grant_donation_amount) * scaleFactor);
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
      var network = document.web3network;

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
      let wei;

      try {
        wei = web3.utils.toWei(String(number));
      } catch (e) {
        // When numbers are too small toWei fails because there's too many decimal places
        wei = Math.round(number * 10 ** 18);
      }

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
        // Prompt web3 login if not connected
        if (!provider) {
          await onConnect();
        }

        // Throw if invalid Gitcoin contribution percentage
        if (Number(this.gitcoinFactorRaw) < 0 || Number(this.gitcoinFactorRaw) > 99) {
          throw new Error('Gitcoin contribution amount must be between 0% and 99%');
        }

        // Throw if there's negative values in the cart
        this.donationInputs.forEach(donation => {
          if (Number(donation.amount) < 0) {
            throw new Error('Cannot have negative donation amounts');
          }
        });

        await window.ethereum.enable();
        const userAddress = (await web3.eth.getAccounts())[0]; // Address of current user

        // Get list of tokens user is donating with
        const selectedTokens = Object.keys(this.donationsToGrants);

        // Token approval and balance checks -------------------------------------------------------
        // For each token, check if an approval is needed, and if so save off the data
        let allowanceData = [];

        for (let i = 0; i < selectedTokens.length; i += 1) {
          const tokenName = selectedTokens[i];
          const tokenDetails = this.getTokenByName(tokenName);

          // If ETH donation no approval is necessary, just check balance
          if (tokenDetails.name === 'ETH') {
            const userEthBalance = await web3.eth.getBalance(userAddress);

            if (new BN(userEthBalance, 10).lt(new BN(this.donationInputsEthAmount, 10))) {
              // Balance is too small, exit checkout flow
              _alert('Insufficient ETH balance to complete checkout', 'error');
              return;
            }
            // Balance is sufficient, continue to next iteration since no approval check
            continue;
          }

          // Get current allowance
          const tokenContract = new web3.eth.Contract(token_abi, tokenDetails.addr);
          const allowance = new BN(await getAllowance(bulkCheckoutAddress, tokenDetails.addr), 10);

          // Get required allowance based on donation amounts
          // We use reduce instead of this.donationsTotal because this.donationsTotal will
          // not have floating point errors, but the actual amounts used will
          const initialValue = new BN('0');
          const requiredAllowance = this.donationInputs.reduce((accumulator, currentValue) => {
            return currentValue.token === tokenDetails.addr
              ? accumulator.add(new BN(currentValue.amount)) // correct token donation
              : accumulator.add(new BN('0')); // ETH donation
          }, initialValue);

          // Check user token balance against requiredAllowance
          const userTokenBalance = await tokenContract.methods.balanceOf(userAddress).call({ from: userAddress });

          if (new BN(userTokenBalance, 10).lt(requiredAllowance)) {
            // Balance is too small, exit checkout flow
            _alert(`Insufficient ${tokenName} balance to complete checkout`, 'error');
            return;
          }

          // If no allowance is needed, continue to next token
          if (allowance.gte(new BN(requiredAllowance))) {
            continue;
          }

          // If we do need to set the allowance, save off the required info
          allowanceData.push({
            allowance: requiredAllowance.toString(),
            contract: tokenContract,
            tokenName
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
          const tokenName = allowanceData[i].tokenName;
          const approvalTx = contract.methods.approve(bulkCheckoutAddress, allowance);

          // We split this into two very similar branches, because on the last approval
          // we send the main donation transaction after we get the transaction hash
          if (i !== allowanceData.length - 1) {
            approvalTx.send({ from: userAddress })
              .on('transactionHash', (txHash) => { // eslint-disable-line no-loop-func
                this.setApprovalTxHash(tokenName, txHash);
              })
              .on('error', (error, receipt) => {
                // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
                this.handleError(error);
              });
          } else {
            approvalTx.send({ from: userAddress })
              .on('transactionHash', (txHash) => { // eslint-disable-line no-loop-func
                indicateMetamaskPopup(true);
                this.setApprovalTxHash(tokenName, txHash);
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

    setApprovalTxHash(tokenName, txHash) {
      this.donationInputs.forEach((donation, index) => {
        if (donation.name === tokenName) {
          this.donationInputs[index].tokenApprovalTxHash = txHash;
        }
      });
    },

    sendDonationTx(userAddress) {
      // Configure our donation inputs
      // We use parse and stringify to avoid mutating this.donationInputs since we use it later
      const bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddress);
      const donationInputs = JSON.parse(JSON.stringify(this.donationInputs)).map(donation => {
        delete donation.name;
        delete donation.grant;
        delete donation.comment;
        delete donation.tokenApprovalTxHash;
        return donation;
      });

      // Remove donations of zero value
      const donationInputsFiltered = donationInputs.filter(donation => {
        return Number(donation.amount) !== 0;
      });

      indicateMetamaskPopup();
      bulkTransaction.methods
        .donate(donationInputsFiltered)
        .send({ from: userAddress, gas: this.donationInputsGasLimit, value: this.donationInputsEthAmount })
        .on('transactionHash', (txHash) => {
          console.log('Donation transaction hash: ', txHash);
          indicateMetamaskPopup(true);
          this.postToDatabase(txHash, userAddress);
          // Clear cart, redirect back to grants page, and show success alert
          localStorage.setItem('contributions_were_successful', 'true');
          localStorage.setItem('contributions_count', String(this.grantData.length));
          var network = document.web3network;
          let timeout_amount = 1500 + (CartData.loadCart().length * 500);

          _alert('Saving contributions. Please do not leave this page.', 'success', 2000);

          setTimeout(function() {
            _alert('Contributions saved', 'success', 1000);
            setTimeout(function() {
              if (network === 'rinkeby') {
                window.location.href = `${window.location.origin}/grants/?network=rinkeby&category=`;
              } else {
                window.location.href = `${window.location.origin}/grants`;
              }
            }, 500);
          }, timeout_amount);
        })
        .on('error', (error, receipt) => {
          // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
          this.handleError(error);
        });
    },

    postToDatabase(txHash, userAddress) {
      // this.donationInputs is the array used for bulk donations
      // We loop through each donation and POST the required data
      const donations = this.donationInputs;
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      for (let i = 0; i < donations.length; i += 1) {
        // Get URL to POST to
        const donation = donations[i];
        const grantId = donation.grant.grant_id;
        const grantSlug = donation.grant.grant_slug;
        const url = `/grants/${grantId}/${grantSlug}/fund`;


        // Get token information
        const tokenName = donation.grant.grant_donation_currency;
        const tokenDetails = this.getTokenByName(tokenName);

        // Gitcoin uses the zero address to represent ETH, but the contract does not. Therefore we
        // get the value of denomination and token_address using the below logic instead of
        // using tokenDetails.addr
        const isEth = tokenName === 'ETH';
        const tokenAddress = isEth ? '0x0000000000000000000000000000000000000000' : tokenDetails.addr;

        // Replace undefined comments with empty strings
        const comment = donation.comment === undefined ? '' : donation.comment;

        // For automatic contributions to Gitcoin, set 'gitcoin-grant-input-amount' to 100.
        // Why 100? Because likely no one will ever use 100% or a normal grant, so using
        // 100 makes it easier to search the DB to find which Gitcoin donations were automatic
        const isAutomatic = donation.grant.isAutomatic;
        const gitcoinGrantInputAmt = isAutomatic ? 100 : Number(this.gitcoinFactorRaw);
        var network = document.web3network;
        // Configure saveSubscription payload
        const saveSubscriptionPayload = new URLSearchParams({
          admin_address: donation.grant.grant_admin_address,
          amount_per_period: Number(donation.grant.grant_donation_amount),
          comment,
          confirmed: false,
          contract_address: donation.grant.grant_contract_address,
          contract_version: donation.grant.grant_contract_version,
          contributor_address: userAddress,
          csrfmiddlewaretoken,
          denomination: tokenAddress,
          frequency_count: 1,
          frequency_unit: 'rounds',
          gas_price: 0,
          'gitcoin-grant-input-amount': gitcoinGrantInputAmt,
          gitcoin_donation_address: gitcoinAddress,
          grant_id: grantId,
          hide_wallet_address: this.hideWalletAddress,
          match_direction: '+',
          network,
          num_periods: 1,
          real_period_seconds: 0,
          recurring_or_not: 'once',
          signature: 'onetime',
          split_tx_id: txHash, // this txhash is our bulk donation hash
          splitter_contract_address: bulkCheckoutAddress,
          sub_new_approve_tx_id: donation.tokenApprovalTxHash,
          subscription_hash: 'onetime',
          token_address: tokenAddress,
          token_symbol: tokenName
        });

        // Configure headers
        const headers = {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        };

        // Define parameter objects for POST request
        const saveSubscriptionParams = {
          method: 'POST',
          headers,
          body: saveSubscriptionPayload
        };

        // Send saveSubscription request
        fetch(url, saveSubscriptionParams)
          .catch(err => {
            this.handleError(err);
          });
      }
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    onResize() {
      this.windowWidth = window.innerWidth;
    },

    lerp(x_lower, x_upper, y_lower, y_upper, x) {
      return y_lower + (((y_upper - y_lower) * (x - x_lower)) / (x_upper - x_lower));
    },

    async valueToDai(amount, tokenSymbol) {
      const url = `${window.location.origin}/sync/get_amount?amount=${amount}&denomination=${tokenSymbol}`;
      const response = await fetch(url);
      const newAmount = await response.json();

      return newAmount.usdt;
    },

    async predictCLRMatch(grant) {
      const rawAmount = Number(grant.grant_donation_amount);
      let amount = await this.valueToDai(rawAmount, grant.grant_donation_currency);

      const clr_prediction_curve_2d = JSON.parse(grant.grant_clr_prediction_curve);
      const clr_prediction_curve = clr_prediction_curve_2d.map(row => row[2]);

      if (amount > 10000) {
        amount = 10000;
      }

      const contributions_axis = [ 0, 1, 10, 100, 1000, 10000 ];
      let predicted_clr = 0;
      let index = 0;

      if (isNaN(amount)) {
        predicted_clr = clr_prediction_curve[index];
      } else if (contributions_axis.indexOf(amount) >= 0) {
        index = contributions_axis.indexOf(amount);
        predicted_clr = clr_prediction_curve[index];
      } else {
        let x_lower = 0;
        let x_upper = 0;
        let y_lower = 0;
        let y_upper = 0;

        if (0 < amount && amount < 1) {
          x_lower = 0;
          x_upper = 1;
          y_lower = clr_prediction_curve[0];
          y_upper = clr_prediction_curve[1];
        } else if (1 < amount && amount < 10) {
          x_lower = 1;
          x_upper = 10;
          y_lower = clr_prediction_curve[1];
          y_upper = clr_prediction_curve[2];
        } else if (10 < amount && amount < 100) {
          x_lower = 10;
          x_upper = 100;
          y_lower = clr_prediction_curve[2];
          y_upper = clr_prediction_curve[3];
        } else if (100 < amount && amount < 1000) {
          x_lower = 100;
          x_upper = 1000;
          y_lower = clr_prediction_curve[3];
          y_upper = clr_prediction_curve[4];
        } else {
          x_lower = 1000;
          x_upper = 10000;
          y_lower = clr_prediction_curve[4];
          y_upper = clr_prediction_curve[5];
        }

        predicted_clr = this.lerp(x_lower, x_upper, y_lower, y_upper, amount);
      }
      return predicted_clr;
    }

  },

  watch: {
    // Use watcher to keep local storage in sync with Vue state
    grantData: {
      async handler() {
        CartData.setCart(this.grantData);
        for (let i = 0; i < this.grantData.length; i += 1) {
          const verification_required_to_get_match = false;

          if (
            (!document.verified && verification_required_to_get_match) ||
            grantData.is_clr_eligible == 'False'
          ) {
            this.grantData[i].grant_donation_clr_match = 0;
          } else {
            const grant = this.grantData[i];
            const matchAmount = await this.predictCLRMatch(grant);

            this.grantData[i].grant_donation_clr_match = matchAmount ? matchAmount.toFixed(2) : 0;
          }
        }
      },
      deep: true
    },

    // We watch this variable to update the robot image
    gitcoinFactorRaw: {
      handler() {
        $('.bot-heart').hide();
        if (Number(this.gitcoinFactorRaw) <= 0) {
          $('#bot-heartbroken').show();
        } else if (Number(this.gitcoinFactorRaw) >= 20) {
          $('#bot-heart-20').show();
        } else if (Number(this.gitcoinFactorRaw) >= 15) {
          $('#bot-heart-15').show();
        } else if (Number(this.gitcoinFactorRaw) >= 10) {
          $('#bot-heart-10').show();
        } else if (Number(this.gitcoinFactorRaw) > 0) {
          $('#bot-heart-5').show();
        }
      }
    }
  },

  async mounted() {
    // Show loading dialog
    this.isLoading = true;
    // Read array of grants in cart from localStorage
    this.grantData = CartData.loadCart();
    // Initialize array of empty comments
    this.comments = this.grantData.map(grant => undefined);
    // Wait until we can load token list
    let elapsedTime = 0;
    let delay = 50; // 50 ms debounce

    while (!this.tokenList) {
      try {
        // Default to mainnet if nothing found after 5s
        var network = elapsedTime >= 5000 ? 'mainnet' : document.web3network;

        if (typeof network != 'undefined') {
          this.tokenList = tokens(network);
        }
      } catch (err) {}
      elapsedTime += delay;
      await this.sleep(delay);
    }
    // Support responsive design
    window.addEventListener('resize', this.onResize);
    // Cart is now ready
    this.isLoading = false;
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
  }
});

var update_cart_title = function() {
  var num_grants = JSON.parse(localStorage.getItem('grants_cart')).length;
  let new_title = 'Grants Cart (' + num_grants + ') | Gitcoin';

  $('title').text(new_title);
};

$(document).ready(function() {
  $(document).on('keyup', 'input[name=telephone]', function(e) {
    var number = $(this).val();

    if (number[0] != '+') {
      number = '+' + number;
      $(this).val(number);
    }
  });


  $(document).on('click', '#verify_offline', function(e) {
    $(this).remove();
    $('#verify_offline_target').css('display', 'block');
  });

  update_cart_title();
});

if (document.getElementById('gc-grants-cart')) {

  const app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-cart',
    data: {
      grantHeaders,
      grantData
    }
  });

  if (document.contxt.github_handle && !document.verified && localStorage.getItem('dismiss-sms-validation') !== 'true') {
    app.$refs.cart.showSMSValidationModal();
  }
}
