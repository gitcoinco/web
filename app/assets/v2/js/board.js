// Time token constants
// Note: "Time Tokens" used to be called "Personal Tokens". To simplify the renaming process,
// variables, classes, and contracts continue to use the old name, but user-facing text uses the
// new name. Personal tokens and Time tokens are the same thing, so you will likely see those two
// phrases used interchangeably throughout the codebase

// Note that this address is also duplicated in profile_tokens.js and app/ptokens/models.py
const factoryAddress = document.contxt.ptoken_factory_address;

let contributorBounties = {};
let pTokens = {};
let bounties = {};
let authProfile = document.contxt.profile_id;
let skills = document.skills;


Vue.mixin({
  data() {
    return {
      selectedRequest: {
        requester: undefined,
        creator: undefined,
        amount: undefined,
        symbol: undefined,
        token_address: undefined,
        id: undefined
      }
    };
  },
  methods: {
    getTokenByName: function(name) {
      if (name === 'ETH') {
        return {
          addr: ETH_ADDRESS,
          name: 'ETH',
          decimals: 18,
          priority: 1
        };
      }
      const network = document.web3network;

      return tokens(network).filter(token => token.name === name)[0];
    },
    fetchBounties: function(type) {
      let vm = this;
      let apiUrlbounties = `/funder_dashboard/${type}/`;
      let getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.$set(vm.bounties, type, response);
        vm.isLoading[type] = false;
      }).catch(function() {
        vm.isLoading[type] = false;
        vm.error[type] = 'Error fetching bounties. Please contact founders@gitcoin.co';
      });
    },
    fetchTokens: function(type) {
      let vm = this;
      let api = `/ptokens/redemptions/${type}/`;
      let getTokens = fetchData (api, 'GET');

      $.when(getTokens).then(function(response) {
        vm.$set(vm.pTokens, type, response);
        vm.isLoading[type] = false;
      }).catch(function() {
        vm.isLoading[type] = false;
        vm.error[type] = 'Error fetching tokens. Please contact founders@gitcoin.co';
      });
    },
    fetchApplicants: function(id, key, type) {
      let vm = this;
      let apiUrlApplicants = `/funder_dashboard/bounties/${id}/`;

      if (vm.bounties[type][key].contributors) {
        return;
      }
      let getApplicants = fetchData (apiUrlApplicants, 'GET');

      $.when(getApplicants).then(function(response) {
        vm.$set(vm.bounties[type][key], 'contributors', response.profiles);
        vm.isLoading[`${type}Contrib`] = false;
      }).catch(function() {
        vm.isLoading[`${type}Contrib`] = false;
      });
    },
    fetchContributorBounties: function(type) {
      let vm = this;
      let apiUrlbounties = `/contributor_dashboard/${type}/`;
      let getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.$set(vm.contributorBounties, type, response);
        vm.isLoading[type] = false;
      }).catch(function() {
        vm.isLoading[type] = false;
        vm.error[type] = 'Error fetching bounties. Please contact founders@gitcoin.co';
      });
    },
    fetchMatchingBounties: function() {
      let vm = this;

      vm.network = document.web3network;
      const apiUrlbounties = `/api/v0.1/bounties/slim/?network=${vm.network}&idx_status=open&applicants=ALL&keywords=${vm.skills}&order_by=-web3_created&offset=0&limit=10`;

      if (vm.matchingBounties.length) {
        return;
      }

      const getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.matchingBounties = response;
        vm.isLoading.matchingBounties = false;
      }).catch(function() {
        vm.isLoading.matchingBounties = false;
      });


    },
    isExpanded(key, type) {
      return this.expandedGroup[type].indexOf(key) !== -1;
    },
    toggleCollapse(key, type) {
      if (this.isExpanded(key, type)) {
        this.expandedGroup[type].splice(this.expandedGroup[type].indexOf(key), 1);
      } else {
        this.expandedGroup[type].push(key);
      }
    },
    startWork(key, bountyPk, profileId) {
      let vm = this;
      let url = `/actions/bounty/${bountyPk}/interest/${profileId}/interested/`;
      let postStartpWork = fetchData (url, 'POST');

      vm.disabledBtn = key;

      $.when(postStartpWork).then(response => {
        vm.contributors.splice(key, 1);
        vm.disabledBtn = '';
        _alert({ message: gettext('Contributor removed from bounty.') }, 'success');
      }, error => {
        vm.disabledBtn = '';
        let msg = error.responseJSON.error || 'got an error. please try again, or contact support@gitcoin.co';

        console.log(error.responseJSON.error);
        _alert({ message: gettext(msg) }, 'danger');
      });
    },
    stopWork(key, bountyPk, profileId, obj, section) {
      let vm = this;
      // let url = `/actions/bounty/${bountyPk}/interest/${profileId}/uninterested/`;
      let url = `/actions/bounty/${bountyPk}/interest/remove/`;

      vm.disabledBtn = key;
      if (window.confirm('Do you want to stop working on this bounty?')) {
        let postStartpWork = fetchData (url, 'POST');

        $.when(postStartpWork).then(response => {
          vm[obj][section].splice(key, 1);
          vm.disabledBtn = '';
          _alert({ message: gettext('Contributor removed from bounty.') }, 'success');
        }, error => {
          vm.disabledBtn = '';
          let msg = error.responseJSON.error || 'got an error. please try again, or contact support@gitcoin.co';

          _alert({ message: gettext(msg) }, 'danger');
        });
      } else {
        vm.disabledBtn = '';
      }
    },
    removeWorker(key, bountyPk, profileId, obj, section) {
      let vm = this;
      let url = `/actions/bounty/${bountyPk}/interest/${profileId}/uninterested/`;

      vm.disabledBtn = key;
      if (window.confirm('Do you want to stop contributor work on this bounty?')) {
        let postStartpWork = fetchData (url, 'POST');

        $.when(postStartpWork).then(response => {
          vm[obj][section].splice(key, 1);
          vm.disabledBtn = '';
          _alert({ message: gettext('Contributor removed from bounty.') }, 'success');
        }, error => {
          vm.disabledBtn = '';
          let msg = error.responseJSON.error || 'got an error. please try again, or contact support@gitcoin.co';

          _alert({ message: gettext(msg) }, 'danger');
        });
      } else {
        vm.disabledBtn = '';
      }
    },
    checkData(persona) {
      let vm = this;

      if (!Object.keys(vm.bounties).length && persona === 'funder') {
        vm.fetchBounties('open');
        vm.fetchBounties('started');
        vm.fetchBounties('submitted');
        vm.fetchBounties('expired');
      }

      if (!Object.keys(vm.contributorBounties).length && persona === 'contributor') {
        vm.fetchContributorBounties('work_in_progress');
        vm.fetchContributorBounties('work_submitted');
        vm.fetchContributorBounties('interested');
      }
      if (persona === 'personal-tokens') {
        vm.fetchTokens('request');
        vm.fetchTokens('accepted');
        vm.fetchTokens('completed');
        vm.fetchTokens('denied');
        vm.fetchTokens('cancelled');
      }
    },
    tabOnLoad(init) {
      let vm = this;
      const params = new URLSearchParams(window.location.search);

      if (document.contxt.persona_is_hunter) {
        vm.checkData('contributor');
      } else {
        vm.checkData('funder');
      }

      if (init && params.get('tab') === 'ptoken') {
        vm.checkData('personal-tokens');
        $('#ptokens-tab').tab('show');
      } else if (document.contxt.persona_is_hunter) {
        $('#contributor-tab').tab('show');
      } else {
        $('#funder-tab').tab('show');
      }

    },
    redirect(url) {
      document.location.href = url;
    },
    async createPToken() {
      const handleError = this.handleError;

      // Hide existing validation errors
      $('#createPTokenName').removeClass('is-invalid');
      $('#createPTokenName ~ .invalid-feedback').hide();
      $('#createPTokenSymbol').removeClass('is-invalid');
      $('#createPTokenSymbol ~ .invalid-feedback').hide();
      $('#createPTokenPrice').removeClass('is-invalid');
      $('#createPTokenPrice ~ .invalid-feedback').hide();
      $('#createPTokenSupply').removeClass('is-invalid');
      $('#createPTokenSupply ~ .invalid-feedback').hide();
      $('#TOSText').removeClass('is-invalid');
      $('#TOSText ~ .invalid-feedback').hide();

      try {
        // TODO: Show loading while deploying
        let price = parseFloat(this.newPToken.price);
        let supply = parseFloat(this.newPToken.supply);
        let stopFlow;

        if (this.newPToken.name === '' || await this.nameExists()) {
          this.$set(this.pToken, 'is_invalid_name', true);
          !stopFlow && (stopFlow = true);
          $('#createPTokenName').addClass('is-invalid');
          $('#createPTokenName ~ .invalid-feedback').show();
        } else {
          this.$set(this.pToken, 'is_invalid_name', false);
        }

        if (this.newPToken.symbol === '' || await this.symbolExists()) {
          this.$set(this.pToken, 'is_invalid_symbol', true);
          !stopFlow && (stopFlow = true);
          $('#createPTokenSymbol').addClass('is-invalid');
          $('#createPTokenSymbol ~ .invalid-feedback').show();
        } else {
          this.$set(this.pToken, 'is_invalid_symbol', false);
        }

        if (isNaN(price) || price <= 0) {
          this.$set(this.pToken, 'is_invalid_price', true);
          !stopFlow && (stopFlow = true);
          $('#createPTokenPrice').addClass('is-invalid');
          $('#createPTokenPrice ~ .invalid-feedback').show();
        } else {
          this.$set(this.pToken, 'is_invalid_price', false);
          this.newPToken.is_invalid_price = false;
        }

        if (isNaN(supply) || supply <= 0) {
          this.$set(this.pToken, 'is_invalid_supply', true);
          !stopFlow && (stopFlow = true);
          $('#createPTokenSupply').addClass('is-invalid');
          $('#createPTokenSupply ~ .invalid-feedback').show();
        } else {
          this.$set(this.pToken, 'is_invalid_supply', false);
        }

        if (!this.newPToken.tos) {
          this.$set(this.pToken, 'is_invalid_tos', true);
          !stopFlow && (stopFlow = true);
          $('#TOSText').addClass('is-invalid');
          $('#TOSText ~ .invalid-feedback').show();
        } else {
          this.$set(this.pToken, 'is_invalid_tos', false);
        }

        if (stopFlow)
          return;

        this.newPToken.deploying = true;
        await this.deployAndSaveToken();
        this.newPToken.deploying = false;
      } catch (err) {
        handleError(err);
      }
    },
    async syncLocalTokenInfo(onSuccess, onError) {
      try {
        // If this user has a ptoken, get the latest info for the frontend
        const myToken = await get_personal_token();

        document.ptoken = Object.assign({}, {
          id: myToken.id,
          name: myToken.name,
          symbol: myToken.symbol,
          price: myToken.price,
          supply: myToken.supply,
          address: myToken.address,
          available: myToken.available,
          purchases: myToken.purchases,
          redemptions: myToken.redemptions,
          tx_status: myToken.tx_status
        });
        this.pToken = document.ptoken;
        if (onSuccess) {
          onSuccess(myToken);
        }
      } catch (err) {
        if (onError) {
          onError(err);
        }
      }
    },
    async nameExists() {
      const name_exists = await ptoken_name_exists(this.newPToken.name);

      this.$set(this.newPToken, 'name_exists', name_exists);
      return name_exists;
    },
    async symbolExists() {
      const symbol_exists = await ptoken_symbol_exists(this.newPToken.symbol);

      this.$set(this.newPToken, 'symbol_exists', symbol_exists);
      return symbol_exists;
    },
    async checkTokenStatus(successMsg, errorMsg) {
      const res = await update_ptokens(); // update all ptokens in DB

      if (res.status === 200) {
        await this.syncLocalTokenInfo((token) => {
          // eslint-disable-next-line no-console
          console.log(successMsg, token); // they have a token, so log those details
        }, (error) => {
          // eslint-disable-next-line no-console
          console.log(successMsg); // they don't have a token, so just log success message
        });

        _alert(successMsg, 'success');

        // For the redemption case, we must hide the "tx pending" modal
        $('#redemptionCompleteReceiptModal').bootstrapModal('hide');
      } else {
        _alert(errorMsg, 'danger');
      }
    },

    async editPToken() {
      try {
        // TODO: Show loading while deploying
        let price = parseFloat(this.pToken.price);
        let supply = parseFloat(this.pToken.supply);
        let supply_locked = document.ptoken.supply - document.ptoken.available;
        let stopFlow;
        const handleError = this.handleError;

        if (isNaN(price) || price <= 0) {
          this.$set(this.pToken, 'is_invalid_price', true);
          this.supplyInvalidMsg = 'Please provide a supply amount';
          !stopFlow && (stopFlow = true);
        } else {
          this.$set(this.pToken, 'is_invalid_price', false);
        }

        if (isNaN(supply) || supply <= 0) {
          this.$set(this.pToken, 'is_invalid_supply', true);
          !stopFlow && (stopFlow = true);
        } else if (supply < supply_locked) {
          this.$set(this.pToken, 'is_invalid_supply', true);
          this.supplyInvalidMsg = `The supply will be less than than ${supply_locked} DAI`;
          !stopFlow && (stopFlow = true);
        } else {
          this.$set(this.pToken, 'is_invalid_supply', false);
        }

        if (!this.pToken.tos) {
          this.$set(this.pToken, 'is_invalid_tos', true);
          !stopFlow && (stopFlow = true);
        } else {
          this.$set(this.pToken, 'is_invalid_tos', false);
        }

        if (stopFlow)
          return;

        this.pToken.deploying = true;
        const { user } = await this.checkWeb3();
        const pTokenId = this.pToken.id;
        const ptoken = await new web3.eth.Contract(document.contxt.ptoken_abi, this.pToken.address);
        const updatePtokenStatusinDatabase = this.updatePtokenStatusinDatabase;

        // Changing price
        if (price !== document.ptoken.price) {
          indicateMetamaskPopup();
          ptoken.methods.updatePrice(web3.utils.toWei(String(price)))
            .send({from: user})
            .on('transactionHash', async function(transactionHash) {
              const network = document.web3network;

              indicateMetamaskPopup(true);
              change_price(pTokenId, price, transactionHash, network);
              document.ptoken.price = price;

              const successMsg = 'The price of your time token has successfully been updated!';
              const errorMsg = 'Oops, something went wrong changing your token price. Please try again or contact support@gitcoin.co';

              await updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg);
            })
            .on('error', function(err) {
              handleError(err);
            });
        }

        // Changing supply
        if (supply !== document.ptoken.supply) {
          if (supply > document.ptoken.supply) {
            // Minting more tokens to increase total supply
            indicateMetamaskPopup();
            ptoken.methods.mint(web3.utils.toWei(String(supply - document.ptoken.supply)))
              .send({from: user})
              .on('transactionHash', async function(transactionHash) {
                const network = document.web3network;

                indicateMetamaskPopup(true);
                mint_tokens(pTokenId, supply, transactionHash, network);
                document.ptoken.supply = supply;
                document.ptoken.available = supply - (document.ptoken.purchases - document.ptoken.redemptions);

                const successMsg = 'The supply of your time token has successfully been increased!';
                const errorMsg = 'Oops, something went wrong increasing your token supply. Please try again or contact support@gitcoin.co';

                await updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg);
              }).on('error', function(err) {
                handleError(err);
              });
          } else {
            // Burning existing tokens to decrease total supply
            indicateMetamaskPopup();
            ptoken.methods.burn(web3.utils.toWei(String(document.ptoken.supply - supply)))
              .send({from: user})
              .on('transactionHash', async function(transactionHash) {
                const network = document.web3network;

                indicateMetamaskPopup(true);
                burn_tokens(pTokenId, supply, transactionHash, network);
                document.ptoken.supply = supply;
                document.ptoken.available = supply - (document.ptoken.purchases - document.ptoken.redemptions);

                const successMsg = 'The supply of your time token has successfully been decreased!';
                const errorMsg = 'Oops, something went wrong decreased your token supply. Please try again or contact support@gitcoin.co';

                await updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg);
              }).on('error', function(err) {
                handleError(err);
              });
          }
        }
        $('#closeEdit').click();
        this.pToken.deploying = false;
      } catch (error) {
        handleError(error);
      }
    },
    async deployAndSaveToken() {
      const vm = this;

      // We currently have DAI addresses hardcoded, so right now pTokens only support
      // being priced in DAI
      const { user, purchaseTokenAddress } = await this.checkWeb3();
      const factory = await new web3.eth.Contract(document.contxt.ptoken_factory_abi, factoryAddress);
      const newPToken = this.newPToken;
      const handleError = this.handleError;
      const updatePtokenStatusinDatabase = this.updatePtokenStatusinDatabase;

      // Deploy on-chain
      indicateMetamaskPopup();
      factory.methods.createPToken(
        newPToken.name,
        newPToken.symbol,
        web3.utils.toWei(String(newPToken.price)),
        web3.utils.toWei(String(newPToken.supply)),
        purchaseTokenAddress
      ).send({
        from: user
      }).on('transactionHash', async function(transactionHash) {
        indicateMetamaskPopup(true);
        // Get url of transaction hash
        const etherscanUrl = document.web3network === 'mainnet'
          ? `https://etherscan.io/tx/${transactionHash}`
          : `https://${document.web3network}.etherscan.io/tx/${transactionHash}`;

        // Hide creation modal and show congratulations modal
        $('#closeCreatePtokenModal').click();
        $('#showCreationSuccessModal').click();
        $('#success-tx').prop('href', etherscanUrl);

        // Update vue state to show that transaction is pending on dashboard
        vm.pToken.tx_status = 'pending';

        // Save to database
        const ptokenReponse = await create_ptoken(
          newPToken.name,
          newPToken.symbol,
          '0x0', // TODO get this from event logs
          newPToken.price,
          newPToken.supply,
          user,
          transactionHash,
          (new Date()).toISOString(),
          document.web3network
        );

        vm.user_has_token = true;
        console.log('Token saved in database', ptokenReponse);
        const successMsg = 'Congratulations, your time token has been created successfully!';
        const errorMsg = 'Oops, something went wrong trying to create your time token. Please try again or contact support@gitcoin.co';

        await updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg);
      }).on('error', function(err) {
        handleError(err);
      });
    },

    /**
     * Waits for the provided transaction to be mined, and after mining triggers a database update.
     * Displays the provided success and error messages on success/failure
     */
    async updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg) {
      console.log('Waiting for transaction to be mined...');
      callFunctionWhenTransactionMined(transactionHash, async() => {
        console.log('Transaction mined, updating database...');
        await this.checkTokenStatus(successMsg, errorMsg);
      });
    },

    checkNetwork() {
      const supportedNetworks = [ 'rinkeby', 'mainnet' ];

      if (!supportedNetworks.includes(document.web3network)) {
        _alert('Unsupported network', 'danger');
        throw new Error('Please connect a wallet');
      }
      return document.web3network;
    },
    async complete(redemptionId, tokenAmount, tokenAddress) {
      const vm = this;
      const updatePtokenStatusinDatabase = this.updatePtokenStatusinDatabase;
      const handleError = this.handleError;
      const redemptionReceiptModal = $('#redemptionCompleteReceiptModal');
      const redemptionEtherscanUrl = $('#redeem-tx');

      try {
        const network = vm.checkNetwork();
        const amount = web3.utils.toWei(String(tokenAmount));
        const [user] = await web3.eth.getAccounts();

        indicateMetamaskPopup();
        const pToken = await new web3.eth.Contract(
          document.contxt.ptoken_abi,
          tokenAddress
        );

        pToken.methods.redeem(amount).send({ from: user })
          .on('transactionHash', async function(transactionHash) {
            indicateMetamaskPopup(true);

            // Show success modal and set Etherscan link
            redemptionReceiptModal.bootstrapModal('show');

            const etherscanUrl = network === 'mainnet'
              ? `https://etherscan.io/tx/${transactionHash}`
              : `https://${network}.etherscan.io/tx/${transactionHash}`;

            redemptionEtherscanUrl.prop('href', etherscanUrl);

            // Save redemption info in database
            const redemption = complete_redemption(
              redemptionId,
              transactionHash,
              TX_STATUS_PENDING,
              user,
              network,
              new Date().toISOString()
            );

            console.log('Redemption saved as pending transaction in database');

            $.when(redemption).then((response) => {
              vm.checkData('personal-tokens');
            });

            const successMsg = 'Congratulations, your redemption was successfully completed!';
            const errorMsg = 'Oops, something went wrong completing the redemption. Please try again or contact support@gitcoin.co';

            await updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg);
            vm.checkData('personal-tokens');
          }).on('error', async(error, receipt) => {
            handleError(error);
            await this.checkTokenStatus(successMsg, errorMsg);
            vm.checkData('personal-tokens');

          });
      } catch (error) {
        handleError(error);
      }
    },
    accept(redemptionId) {
      const redemption = accept_redemption(redemptionId);
      const vm = this;

      $.when(redemption).then((response) => {
        vm.checkData('personal-tokens');
        console.log(response);
      });
    },
    cancel(redemptionId) {
      const redemption = denied_redemption(redemptionId);
      const vm = this;

      $.when(redemption).then((response) => {
        vm.checkData('personal-tokens');
        console.log(response);
      });
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
      indicateMetamaskPopup(true);
    },

    async checkWeb3() {
      if (!web3) {
        throw new Error('Please connect a wallet');
      }
      [user] = await web3.eth.getAccounts();

      if (document.web3network === 'rinkeby' || document.web3network === 'mainnet') {
        purchaseTokenAddress = this.getTokenByName('DAI').addr;
      } else {
        throw new Error('Unsupported network');
      }

      return { user, purchaseTokenAddress };
    },

    // These two methods are used to provide access to the specified token details
    // in the redemption accept and deny modals
    setSelectedRequest(token) {
      this.selectedRequest.requester = token.requester;
      this.selectedRequest.creator = token.creator;
      this.selectedRequest.amount = token.amount;
      this.selectedRequest.token_address = token.token_address;
      this.selectedRequest.token_symbol = token.token_symbol;
      this.selectedRequest.id = token.id;
    },

    resetSelectedRequest() {
      this.selectedRequest.requester = undefined;
      this.selectedRequest.creator = undefined;
      this.selectedRequest.amount = undefined;
      this.selectedRequest.token_address = undefined;
      this.selectedRequest.token_symbol = undefined;
      this.selectedRequest.id = undefined;
    }
  }
});


if (document.getElementById('gc-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-board',
    data: {
      network: document.web3network,
      has_ptoken_auth: document.has_ptoken_auth,
      user_has_token: document.user_has_token,
      bounties: bounties,
      openBounties: [],
      submittedBounties: [],
      expiredBounties: [],
      contributors: [],
      contributorBounties: contributorBounties,
      pTokens: pTokens,
      expandedGroup: {'submitted': [], 'open': [], 'started': [], 'bountiesMatch': []},
      disabledBtn: false,
      authProfile: authProfile,
      skills: skills,
      matchingBounties: [],
      pToken: Object.assign({}, document.ptoken),
      supplyInvalidMsg: 'Please provide a supply amount',
      current_user: document.contxt.github_handle,
      newPToken: {
        name: '',
        symbol: '',
        price: '',
        supply: '',
        deploying: false
      },
      isLoading: {
        'open': true,
        'openContrib': true,
        'started': true,
        'startedContrib': true,
        'submitted': true,
        'submittedContrib': true,
        'expired': true,
        'work_in_progress': true,
        'interested': true,
        'work_submitted': true,
        'matchingBounties': true
      },
      error: {
        'open': '',
        'openContrib': '',
        'started': '',
        'startedContrib': '',
        'submitted': '',
        'submittedContrib': '',
        'expired': '',
        'work_in_progress': '',
        'interested': '',
        'work_submitted': ''
      }
    },
    async mounted() {
      this.tabOnLoad(true);
      if (this.pToken && this.pToken.tx_status === TX_STATUS_PENDING) {
        await this.checkTokenStatus();
      }

    }
  });
}

Vue.filter('truncate', (account, num) => {
  num = !num ? num = 4 : num;
  return account.substr(0, num + 2) + '\u2026' + account.substr(-num);
});

Vue.filter('moment', (date) => {
  moment.locale('en');
  return moment.utc(date).fromNow();
});

Vue.filter('humanizeEth', (number) => {
  return parseInt(number, 10) / Math.pow(10, 18);
});
