let appFormBounty;

window.addEventListener('dataWalletReady', function(e) {
  appFormBounty.network = networkName;
  appFormBounty.form.funderAddress = selectedAccount;
}, false);

Vue.component('v-select', VueSelect.VueSelect);
Vue.mixin({
  methods: {
    estHoursValidator: function() {
      this.form.hours = parseFloat(this.form.hours || 0);
      this.form.hours = Math.ceil(this.form.hours);
      this.calcValues('token');
    },
    getIssueDetails: function(url) {
      let vm = this;

      if (!url) {
        vm.$set(vm.errors, 'issueDetails', undefined);
        vm.form.issueDetails = null;
        return vm.form.issueDetails;
      }

      if (url.indexOf('github.com/') < 0) {
        vm.form.issueDetails = undefined;
        vm.$set(vm.errors, 'issueDetails', 'Please paste a github issue url');
        return;
      }

      if (url.indexOf('/pull/') > 0) {
        vm.$set(vm.errors, 'issueDetails', 'Please paste a github issue url and not a PR');
        return;
      }

      let ghIssueUrl = new URL(url);

      vm.orgSelected = ghIssueUrl.pathname.split('/')[1].toLowerCase();

      if (vm.checkBlocked(vm.orgSelected)) {
        vm.$set(vm.errors, 'issueDetails', 'This repo is not bountyable at the request of the maintainer.');
        vm.form.issueDetails = undefined;
        return;
      }
      vm.$delete(vm.errors, 'issueDetails');

      const apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url.trim())}&duplicates=true&network=${vm.network}`;

      vm.form.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        if (!Object.keys(response).length) {
          return vm.$set(vm.errors, 'issueDetails', 'Nothing found. Please check the issue URL.');
        }

        vm.form.issueDetails = response;
        // vm.$set(vm.errors, 'issueDetails', undefined);
      }).catch((err) => {
        console.log(err);
        vm.form.issueDetails = undefined;
        vm.$set(vm.errors, 'issueDetails', err.responseJSON.message);
      });

    },
    getTokens: function() {
      let vm = this;
      const apiUrlTokens = '/api/v1/tokens/';
      const getTokensData = fetchData(apiUrlTokens, 'GET');

      $.when(getTokensData).then((response) => {
        vm.tokens = response;
        vm.form.token = vm.filterByChainId[0];
        vm.getAmount(vm.form.token.symbol);

      }).catch((err) => {
        console.log(err);
      });

    },
    getBinanceSelectedAccount: async function() {
      let vm = this;

      try {
        vm.form.funderAddress = await binance_utils.getSelectedAccount();
      } catch (error) {
        vm.funderAddressFallback = true;
      }
    },
    getAmount: function(token) {
      let vm = this;

      if (!token) {
        return;
      }
      const apiUrlAmount = `/sync/get_amount?amount=1&denomination=${token}`;
      const getAmountData = fetchData(apiUrlAmount, 'GET');

      $.when(getAmountData).then(tokens => {
        vm.coinValue = tokens[0].usdt;
        vm.calcValues('usd');

      }).catch((err) => {
        console.log(err);
      });
    },
    calcValues: function(direction) {
      let vm = this;

      if (direction == 'usd') {
        let usdValue = vm.form.amount * vm.coinValue;

        vm.form.amountusd = Number(usdValue.toFixed(2));
      } else {
        vm.form.amount = Number(vm.form.amountusd * 1 / vm.coinValue).toFixed(4);
      }

    },
    addKeyword: function(item) {
      let vm = this;

      vm.form.keywords.push(item);
    },
    validateFunderAddress: function() {
      let vm = this;
      let isValid = true;

      switch (vm.chainId) {
        case '1995': {
          // nervos
          const ADDRESS_REGEX = new RegExp('^(ckb){1}[0-9a-zA-Z]{43,92}$');
          const isNervosValid = ADDRESS_REGEX.test(vm.form.funderAddress);
    
          if (!isNervosValid && !vm.form.funderAddress.toLowerCase().startsWith('0x')) {
            isValid = false;
          }
          break;
        }

        case '50797': {
          // tezos
          const ADDRESS_REGEX = new RegExp('^(tz1|tz2|tz3)[0-9a-zA-Z]{33}$');
          const isTezosValid = ADDRESS_REGEX.test(vm.form.funderAddress);

          if (!isTezosValid) {
            isValid = false;
          }
          break;
        }

        case '0': {
          // btc
          const ADDRESS_REGEX = new RegExp('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$');
          const BECH32_REGEX = new RegExp('^bc1[ac-hj-np-zAC-HJ-NP-Z02-9]{11,71}$');
          const valid_legacy = ADDRESS_REGEX.test(vm.form.funderAddress);
          const valid_segwit = BECH32_REGEX.test(vm.form.funderAddress);
    
          if (!valid_legacy && !valid_segwit) {
            isValid = false;
          }
          break;
        }

        case '270895': {
          // casper
          let addr = vm.form.funderAddress;

          if (!addr.toLowerCase().startsWith('01') && !addr.toLowerCase().startsWith('02')) {
            isValid = false;
          }
          break;
        }

        // include validation for other chains here
      }

      return isValid;
    },
    checkForm: async function(e) {
      let vm = this;

      vm.submitted = true;
      vm.errors = {};

      if (!vm.form.keywords.length) {
        vm.$set(vm.errors, 'keywords', 'Please select the prize keywords');
      }
      if (!vm.form.experience_level || !vm.form.project_length || !vm.form.bounty_type) {
        vm.$set(vm.errors, 'experience_level', 'Please select the details options');
      }
      if (!vm.chainId) {
        vm.$set(vm.errors, 'chainId', 'Please select an option');
      }
      if (!vm.form.issueDetails || vm.form.issueDetails < 1) {
        vm.$set(vm.errors, 'issueDetails', 'Please input a GitHub issue');
      }
      if (vm.form.bounty_categories.length < 1) {
        vm.$set(vm.errors, 'bounty_categories', 'Select at least one category');
      }
      if (!vm.form.funderAddress) {
        vm.$set(vm.errors, 'funderAddress', 'Fill the owner wallet address');
      }
      if (!vm.validateFunderAddress()) {
        vm.$set(vm.errors, 'funderAddress', `Please enter a valid ${vm.form.token.symbol} address`);
      }
      if (!vm.form.project_type) {
        vm.$set(vm.errors, 'project_type', 'Select the project type');
      }
      if (!vm.form.permission_type) {
        vm.$set(vm.errors, 'permission_type', 'Select the permission type');
      }
      if (!vm.form.terms) {
        vm.$set(vm.errors, 'terms', 'You need to accept the terms');
      }
      if (!vm.form.termsPrivacy) {
        vm.$set(vm.errors, 'termsPrivacy', 'You need to accept the terms');
      }
      if (Object.keys(vm.errors).length) {
        return false;
      }
    },
    web3Type() {
      let vm = this;
      let type;

      switch (vm.chainId) {
        case '1':
          // ethereum
          type = 'web3_modal';
          break;
        case '30':
          // rsk
          type = 'rsk_ext';
          break;
        case '50':
          // xinfin
          type = 'xinfin_ext';
          break;
        case '59':
        case '58':
          // 58 - polkadot, 59 - kusama
          type = 'polkadot_ext';
          break;
        case '56':
          // binance
          type = 'binance_ext';
          break;
        case '1000':
          // harmony
          type = 'harmony_ext';
          break;
        case '1995':
          // nervos
          type = 'nervos_ext';
          break;
        case '1001':
          // algorand
          type = 'algorand_ext';
          break;
        case '1935':
          // sia
          type = 'sia_ext';
          break;
        case '50797':
          // tezos
          type = 'tezos_ext';
          break;
        case '270895':
          // casper
          type = 'casper_ext';
          break;
        case '666':
          // paypal
          type = 'fiat';
          break;
        case '0': // bitcoin
        case '61': // ethereum classic
        case '102': // zilliqa
        case '600': // filecoin
        case '42220': // celo mainnet
        case '44786': // celo alfajores tesnet
        case '717171': // other
          type = 'qr';
          break;
        default:
          type = 'web3_modal';
      }

      vm.form.web3_type = type;
      return type;
    },
    getParams: async function() {
      let vm = this;

      let params = new URLSearchParams(window.location.search);

      if (params.has('invite')) {
        vm.expandedGroup.reserve = [1];
      }

      if (params.has('reserved')) {
        vm.expandedGroup.reserve = [1];
        await vm.getUser(null, params.get('reserved'), true);
      }

      let url;

      if (params.has('url')) {
        url = params.get('url');
        vm.form.issueUrl = url;
        vm.getIssueDetails(url);
      }

      if (params.has('source')) {
        url = params.get('source');
        vm.form.issueUrl = url;
        vm.getIssueDetails(url);
      }
    },
    showQuickStart: function(force) {
      let quickstartDontshow = localStorage['quickstart_dontshow'] ? JSON.parse(localStorage['quickstart_dontshow']) : false;

      if (quickstartDontshow !== true || force) {
        fetch('/bounty/quickstart')
          .then(function(response) {
            return response.text();
          }).then(function(html) {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const guide = doc.querySelector('.btn-closeguide');

            doc.querySelector('.show_video').href = 'https://www.youtube.com/watch?v=m1X0bDpVcf4';
            doc.querySelector('.show_video').target = '_blank';

            guide.dataset.dismiss = 'modal';

            const docArticle = doc.querySelector('.content').innerHTML;
            const content = $.parseHTML(
              `<div id="gitcoin_updates" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
                <div class="modal-dialog modal-xl" style="max-width:95%">
                  <div class="modal-content px-4 py-3">
                    <div class="col-12">
                      <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                    </div>
                    ${docArticle}
                    <div class="col-12 my-4 d-flex justify-content-around">
                      <button type="button" class="btn btn-primary" data-dismiss="modal" aria-label="Close">Close</button>
                    </div>
                  </div>
                </div>
              </div>`);

            $(content).appendTo('body');
            document.getElementById('dontshow').checked = quickstartDontshow;
            $('#gitcoin_updates').bootstrapModal('show');

            $(document).on('change', '#dontshow', function(e) {
              if ($(this)[0].checked) {
                localStorage['quickstart_dontshow'] = true;
              } else {
                localStorage['quickstart_dontshow'] = false;
              }
            });
          });

        $(document, '#gitcoin_updates').on('hidden.bs.modal', function(e) {
          $('#gitcoin_updates').remove();
          $('#gitcoin_updates').bootstrapModal('dispose');
        });
      }
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
    updateDate(date) {
      let vm = this;

      vm.form.expirationTimeDelta = date.format('MM/DD/YYYY');

    },
    userSearch(search, loading) {
      let vm = this;

      if (search.length < 3) {
        return;
      }
      loading(true);
      vm.getUser(loading, search);

    },
    getUser: async function(loading, search, selected) {
      let vm = this;
      let myHeaders = new Headers();
      let url = `/api/v0.1/users_search/?token=${currentProfile.githubToken}&term=${escape(search)}`;

      myHeaders.append('X-Requested-With', 'XMLHttpRequest');
      return new Promise(resolve => {

        fetch(url, {
          credentials: 'include',
          headers: myHeaders
        }).then(res => {
          res.json().then(json => {
            vm.usersOptions = json;
            if (selected) {
              vm.$set(vm.form, 'reservedFor', vm.usersOptions[0].text);
            }
            resolve();
          });
          if (loading) {
            loading(false);
          }
        });
      });
    },
    checkBlocked(org) {
      let vm = this;
      let blocked = vm.blockedUrls.toLocaleString().toLowerCase().split(',');

      return blocked.indexOf(org.toLowerCase()) > -1;
    },
    featuredValue() {
      let vm = this;
      const apiUrlAmount = `/sync/get_amount?amount=${vm.usdFeaturedPrice}&denomination=USDT`;
      const getAmountData = fetchData(apiUrlAmount, 'GET');

      $.when(getAmountData).then(value => {
        vm.ethFeaturedPrice = value[0].eth.toFixed(4);

      }).catch((err) => {
        console.log(err);
      });
    },
    payFeaturedBounty: async function() {
      let vm = this;

      if (!provider) {
        onConnect();
        return false;
      }
      return new Promise(resolve =>
        web3.eth.sendTransaction({
          to: '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
          from: selectedAccount,
          value: web3.utils.toWei(String(vm.ethFeaturedPrice), 'ether'),
          gas: web3.utils.toHex(318730),
          gasLimit: web3.utils.toHex(318730)
        }, function(error, result) {
          if (error) {
            _alert({ message: gettext('Unable to upgrade to featured bounty. Please try again.') }, 'danger');
            console.log(error);
          } else {
            saveAttestationData(
              result,
              vm.ethFeaturedPrice,
              '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
              'featuredbounty'
            );
            resolve();
          }
        })
      );
    },
    payFees: async function() {
      let vm = this;
      const toAddress = '0x88c62f1695DD073B43dB16Df1559Fda841de38c6';

      if (!provider) {
        onConnect();
        return false;
      }
      return new Promise(resolve => {

        if (vm.form.token.symbol === 'ETH') {
          web3.eth.sendTransaction({
            to: toAddress,
            from: selectedAccount,
            value: BigInt(vm.totalAmount.totalFee.toFixed(18) * Math.pow(10, 18)).toString()
          }).once('transactionHash', (txnHash, errors) => {

            console.log(txnHash, errors);

            if (errors) {
              _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'danger');
            } else {
              vm.form.feeTxId = txnHash;
              saveAttestationData(
                txnHash,
                vm.totalAmount.totalFee,
                '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
                'bountyfee'
              );
              resolve();
            }
          });
        } else if (vm.form.token.chainId === 1) {
          const amountInWei = vm.totalAmount.totalFee * 1.0 * Math.pow(10, vm.form.token.decimals);
          const amountAsString = new web3.utils.BN(BigInt(amountInWei)).toString();
          const token_contract = new web3.eth.Contract(token_abi, vm.form.token.address);

          token_contract.methods.transfer(toAddress, web3.utils.toHex(amountAsString)).send({from: selectedAccount},
            function(error, txnId) {
              if (error) {
                _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'danger');
              } else {
                resolve();
              }
            }
          );

        }
      });

    },
    submitForm: async function(event) {
      event.preventDefault();
      let vm = this;

      vm.checkForm(event);

      if (!provider && vm.chainId === '1') {
        onConnect();
        return false;
      }

      if (Object.keys(vm.errors).length) {
        return false;
      }
      if (vm.bountyFee > 0 && !vm.subscriptionActive) {
        await vm.payFees();
      }
      if (vm.form.featuredBounty && !vm.subscriptionActive) {
        await vm.payFeaturedBounty();
      }
      const metadata = {
        issueTitle: vm.form.issueDetails.title,
        issueDescription: vm.form.issueDetails.description,
        issueKeywords: vm.form.keywords.join(),
        githubUsername: vm.form.githubUsername,
        notificationEmail: vm.form.notificationEmail,
        fullName: vm.form.fullName,
        experienceLevel: vm.form.experience_level,
        projectLength: vm.form.project_length,
        bountyType: vm.form.bounty_type,
        estimatedHours: vm.form.hours,
        fundingOrganisation: vm.form.fundingOrganisation,
        eventTag: vm.form.eventTag,
        is_featured: vm.form.featuredBounty ? '1' : undefined,
        repo_type: 'public',
        featuring_date: vm.form.featuredBounty && ((new Date().getTime() / 1000) | 0) || 0,
        reservedFor: '',
        releaseAfter: '',
        tokenName: vm.form.token.symbol,
        invite: [],
        bounty_categories: vm.form.bounty_categories.join(),
        activity: '',
        chain_id: vm.chainId
      };

      const params = {
        'title': metadata.issueTitle,
        'amount': vm.form.amount,
        'value_in_token': vm.form.amount * 10 ** vm.form.token.decimals,
        'token_name': metadata.tokenName,
        'token_address': vm.form.token.address,
        'bounty_type': metadata.bountyType,
        'project_length': metadata.projectLength,
        'estimated_hours': metadata.estimatedHours,
        'experience_level': metadata.experienceLevel,
        'github_url': vm.form.issueUrl,
        'bounty_owner_email': metadata.notificationEmail,
        'bounty_owner_github_username': metadata.githubUsername,
        'bounty_owner_name': metadata.fullName, // ETC-TODO REMOVE ?
        'bounty_reserved_for': metadata.reservedFor,
        'release_to_public': metadata.releaseAfter,
        'expires_date': vm.checkboxes.neverExpires ? 9999999999 : moment(vm.form.expirationTimeDelta).utc().unix(),
        'metadata': JSON.stringify(metadata),
        'raw_data': {}, // ETC-TODO REMOVE ?
        'network': vm.network,
        'issue_description': metadata.issueDescription,
        'funding_organisation': metadata.fundingOrganisation,
        'balance': vm.form.amount * 10 ** vm.form.token.decimals, // ETC-TODO REMOVE ?
        'project_type': vm.form.project_type,
        'permission_type': vm.form.permission_type,
        'bounty_categories': metadata.bounty_categories,
        'repo_type': metadata.repo_type,
        'is_featured': metadata.is_featured,
        'featuring_date': metadata.featuring_date,
        'fee_amount': vm.totalAmount.totalFee,
        'fee_tx_id': vm.form.feeTxId,
        'coupon_code': vm.form.couponCode,
        'privacy_preferences': JSON.stringify({
          show_email_publicly: vm.form.showEmailPublicly
        }),
        'attached_job_description': vm.form.jobDescription,
        'eventTag': metadata.eventTag,
        'auto_approve_workers': vm.form.auto_approve_workers,
        'web3_type': vm.web3Type(),
        'activity': metadata.activity,
        'bounty_owner_address': vm.form.funderAddress
      };

      vm.sendBounty(params);

    },
    sendBounty(data) {
      let vm = this;

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Create Bounty', 'click', 'Bounty Funder');
      }

      const apiUrlBounty = '/api/v1/bounty/create';
      const postBountyData = fetchData(apiUrlBounty, 'POST', data);

      $.when(postBountyData).then((response) => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
          window.location.href = response.bounty_url;
        } else if (response.status == 304) {
          _alert('Bounty already exists for this github issue.', 'danger');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        } else {
          _alert(`Unable to create a bounty. ${response.message}`, 'danger');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        }

      }).catch((err) => {
        console.log(err);
        _alert('Unable to create a bounty. Please try again later', 'danger');
      });

    }
  },
  computed: {
    totalAmount: function() {
      let vm = this;
      let fee;

      if (vm.chainId === '1' && !vm.subscriptionActive) {
        vm.bountyFee = document.FEE_PERCENTAGE;
        fee = Number(vm.bountyFee) / 100.0;
      } else {
        vm.bountyFee = 0;
        fee = 0;
      }
      let totalFee = Number(vm.form.amount) * fee;
      let total = Number(vm.form.amount) + totalFee;

      return {'totalFee': totalFee, 'total': total };
    },
    totalTx: function() {
      let vm = this;
      let numberTx = 0;

      if (vm.chainId === '1' && !vm.subscriptionActive) {
        numberTx += vm.bountyFee > 0 ? 1 : 0;
      } else {
        numberTx = 0;
      }

      if (!vm.subscriptionActive) {
        numberTx += vm.form.featuredBounty ? 1 : 0;
      }

      return numberTx;

    },
    filterOrgSelected: function() {
      if (!this.orgSelected) {
        return;
      }
      return `/dynamic/avatar/${this.orgSelected}`;
    },
    successRate: function() {
      let rate;

      if (!this.form.amountusd) {
        return;
      }

      rate = ((this.form.amountusd / this.form.hours) * 100 / 120).toFixed(0);
      if (rate > 100) {
        rate = 100;
      }
      return rate;

    },
    sortByPriority: function() {
      return this.tokens.sort(function(a, b) {
        return b.priority - a.priority;
      });
    },
    filterByNetwork: function() {
      const vm = this;

      if (vm.network == '') {
        return vm.sortByPriority;
      }
      return vm.sortByPriority.filter((item)=>{

        return item.network.toLowerCase().indexOf(vm.network.toLowerCase()) >= 0;
      });
    },
    filterByChainId: function() {
      const vm = this;
      let result;

      if (vm.chainId == '') {
        result = vm.filterByNetwork;
      } else {
        result = vm.filterByNetwork.filter((item) => {
          return String(item.chainId) === vm.chainId;
        });
      }
      return result;
    }
  },
  watch: {
    form: {
      deep: true,
      handler(newVal, oldVal) {
        if (this.dirty && this.submitted) {
          this.checkForm();
        }
        this.dirty = true;
      }

    },
    chainId: async function(val) {
      if (!provider && val === '1') {
        await onConnect();
      }

      if (val === '56') {
        this.getBinanceSelectedAccount();
      }

      this.getTokens();
    }
  }
});

if (document.getElementById('gc-hackathon-new-bounty')) {
  appFormBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-hackathon-new-bounty',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {

        tokens: [],
        network: 'mainnet',
        chainId: '',
        funderAddressFallback: false,
        checkboxes: {'terms': false, 'termsPrivacy': false, 'neverExpires': true, 'hiringRightNow': false },
        expandedGroup: {'reserve': [], 'featuredBounty': []},
        errors: {},
        usersOptions: [],
        bountyFee: document.FEE_PERCENTAGE,
        orgSelected: '',
        subscriptions: document.subscriptions,
        subscriptionActive: document.subscriptions.length || document.contxt.is_pro,
        coinValue: null,
        usdFeaturedPrice: 12,
        ethFeaturedPrice: null,
        blockedUrls: document.blocked_urls,
        dirty: false,
        submitted: false,
        form: {
          expirationTimeDelta: moment().add(1, 'month').format('MM/DD/YYYY'),
          featuredBounty: false,
          fundingOrganisation: '',
          issueDetails: undefined,
          issueUrl: '',
          githubUsername: document.contxt.github_handle,
          notificationEmail: document.contxt.email,
          showEmailPublicly: '1',
          auto_approve_workers: false,
          fullName: document.contxt.name,
          hours: '1',
          bounty_categories: [],
          project_type: '',
          permission_type: '',
          keywords: [],
          amount: 0.001,
          amountusd: null,
          token: {},
          terms: false,
          termsPrivacy: false,
          feeTxId: null,
          couponCode: document.coupon_code
        }
      };
    },
    mounted() {
      this.getParams();
      this.showQuickStart();
      this.getTokens();
      this.featuredValue();
    }
  });
}
