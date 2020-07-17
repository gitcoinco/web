let appFormBounty;

window.addEventListener('dataWalletReady', function(e) {
  appFormBounty.network = networkName;
  appFormBounty.form.funderAddress = selectedAccount;
}, false);

Vue.component('v-select', VueSelect.VueSelect);
Vue.mixin({
  methods: {
    getIssueDetails: function(url) {
      let vm = this;

      if (!url) {
        vm.$set(vm.errors, 'issueDetails', undefined);
        vm.form.issueDetails = null;
        return vm.form.issueDetails;
      }

      if (url.indexOf('github.com/') < 0) {
        vm.form.issueDetails = null;
        vm.$set(vm.errors, 'issueDetails', 'Please paste a github issue url');
        return;
      }

      let ghIssueUrl = new URL(url);

      vm.orgSelected = '';

      const apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url.trim())}`;

      vm.$set(vm.errors, 'issueDetails', undefined);

      vm.form.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        vm.orgSelected = ghIssueUrl.pathname.split('/')[1].toLowerCase();
        // vm.orgSelected = vm.filterOrgSelected(ghIssueUrl.pathname.split('/')[1]);
        vm.form.issueDetails = response;
        vm.$set(vm.errors, 'issueDetails', undefined);
      }).catch((err) => {
        console.log(err);
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
        // vm.errorIssueDetails = err.responseJSON.message;
      });

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
    checkForm: async function(e) {
      let vm = this;

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
      if (!vm.form.project_type) {
        vm.$set(vm.errors, 'project_type', 'Select the project type');
      }
      if (!vm.form.permission_type) {
        vm.$set(vm.errors, 'permission_type', 'Select the permission type');
      }
      if (!vm.checkboxes.terms || !vm.checkboxes.termsPrivacy) {
        vm.$set(vm.errors, 'terms', 'You need to accept the terms');
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
        case '666':
          // paypal
          type = 'fiat';
          break;
        case '61': // ethereum classic
        case '102': // zilliqa
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
    showQuickStart: function(force) {
      let quickstartDontshow = localStorage['quickstart_dontshow'] ? JSON.parse(localStorage['quickstart_dontshow']) : false;

      if (quickstartDontshow !== true || force) {
        fetch('/bounty/quickstart')
          .then(function(response) {
            return response.text();
          }).then(function(html) {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, 'text/html');

            doc.querySelector('.show_video').href = 'https://www.youtube.com/watch?v=m1X0bDpVcf4';
            doc.querySelector('.show_video').target = '_blank';
            doc.querySelector('.btn-closeguide').dataset.dismiss = 'modal';

            let docArticle = doc.querySelector('.content').innerHTML;
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
                      <button type="button" class="btn btn-gc-blue" data-dismiss="modal" aria-label="Close">Close</button>
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
      let myHeaders = new Headers();

      if (search.length < 3) {
        return;
      }

      myHeaders.append('X-Requested-With', 'XMLHttpRequest');

      let url = `/api/v0.1/users_search/?token=${currentProfile.githubToken}&term=${escape(search)}`;

      loading(true);
      fetch(url, {
        credentials: 'include',
        headers: myHeaders
      }).then(res => {
        res.json().then(json => (vm.usersOptions = json));
        loading(false);
      });

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
          to: '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
          from: selectedAccount,
          value: web3.utils.toWei(String(vm.ethFeaturedPrice), 'ether'),
          gas: web3.utils.toHex(318730),
          gasLimit: web3.utils.toHex(318730)
        }, function(error, result) {
          if (error) {
            _alert({ message: gettext('Unable to upgrade to featured bounty. Please try again.') }, 'error');
            console.log(error);
          } else {
            saveAttestationData(
              result,
              vm.ethFeaturedPrice,
              '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
              'featuredbounty'
            );
            resolve();
          }
        })
      );
    },
    payFees: async function() {
      let vm = this;
      const toAddress = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
      // const fee = Number((Number(data.amount) * FEE_PERCENTAGE).toFixed(4));

      if (!provider) {
        onConnect();
        return false;
      }
      return new Promise(resolve => {

        if (vm.form.token.symbol === 'ETH') {
          web3.eth.sendTransaction({
            to: toAddress,
            from: selectedAccount,
            value: web3.utils.toWei(String(vm.totalAmount.totalFee), 'ether')
          }).once('transactionHash', (txnHash, errors) => {

            console.log(txnHash, errors);

            if (errors) {
              _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
            } else {

              saveAttestationData(
                txnHash,
                vm.totalAmount.totalFee,
                '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
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
                _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
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
      if (vm.bountyFee > 0) {
        await vm.payFees();
      }
      if (vm.form.featuredBounty) {
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
        'fee_amount': 0,
        'fee_tx_id': null,
        'coupon_code': vm.form.couponCode,
        'privacy_preferences': JSON.stringify({
          show_email_publicly: vm.form.showEmailPublicly
        }),
        'attached_job_description': vm.form.jobDescription,
        'eventTag': metadata.eventTag,
        'auto_approve_workers': 'True',
        'web3_type': vm.web3Type(),
        'activity': metadata.activity,
        'bounty_owner_address': vm.form.funderAddress
      };

      vm.sendBounty(params);

    },
    sendBounty(data) {
      let vm = this;

      const apiUrlBounty = '/api/v1/bounty/create';
      const postBountyData = fetchData(apiUrlBounty, 'POST', data);

      $.when(postBountyData).then((response) => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
          window.location.href = response.bounty_url;
        } else if (response.status == 304) {
          _alert('Bounty already exists for this github issue.', 'error');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        } else {
          _alert(`Unable to create a bounty. ${response.message}`, 'error');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        }

      }).catch((err) => {
        console.log(err);
        _alert('Unable to create a bounty. Please try again later', 'error');
      });

    }
  },
  computed: {
    totalAmount: function() {
      let vm = this;
      let fee;

      if (vm.chainId !== '1') {
        fee = 0;
      } else {
        fee = Number(vm.bountyFee) / 100.0;
      }
      let totalFee = Number(vm.form.amount) * fee;
      let total = Number(vm.form.amount) + totalFee;

      return {'totalFee': totalFee, 'total': total };
    },
    filterOrgSelected: function() {
      if (!this.orgSelected) {
        return;
      }
      return `/dynamic/avatar/${this.orgSelected}`;
      // return this.sponsors.filter((sponsor) => {
      //   return sponsor.handle.toLowerCase() === this.orgSelected.toLowerCase();
      // });
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

      vm.form.token = {};
      if (vm.chainId == '') {
        result = vm.filterByNetwork;
      } else {
        result = vm.filterByNetwork.filter((item) => {
          return String(item.chainId) === vm.chainId;
        });
      }
      vm.form.token = result[0];
      return result;
    }
  },
  watch: {
    chainId: async function(val) {
      if (!provider && val === '1') {
        await onConnect();
      }

      this.getTokens();
      // await this.checkForm();
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
        checkboxes: {'terms': false, 'termsPrivacy': false, 'neverExpires': true, 'hiringRightNow': false },
        expandedGroup: {'reserve': [], 'featuredBounty': []},
        errors: {},
        usersOptions: [],
        bountyFee: document.FEE_PERCENTAGE,
        orgSelected: '',
        coinValue: null,
        usdFeaturedPrice: 12,
        ethFeaturedPrice: null,
        form: {
          expirationTimeDelta: moment().add(1, 'month').format('MM/DD/YYYY'),
          featuredBounty: false,
          fundingOrganisation: '',
          issueDetails: undefined,
          issueUrl: '',
          githubUsername: document.contxt.github_handle,
          notificationEmail: document.contxt.email,
          showEmailPublicly: '1',
          fullName: document.contxt.name,
          hours: '1',
          bounty_categories: [],
          project_type: '',
          permission_type: '',
          keywords: [],
          amount: 0.001,
          amountusd: null,
          token: {},
          couponCode: document.coupon_code
        }
      };
    },
    mounted() {
      this.showQuickStart();
      this.getTokens();
      this.featuredValue();
    }
  });
}
