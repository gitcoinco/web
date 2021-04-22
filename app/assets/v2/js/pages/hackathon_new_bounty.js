let appFormHackathon;

window.addEventListener('dataWalletReady', function(e) {
  appFormHackathon.network = networkName;
  appFormHackathon.form.funderAddress = selectedAccount;
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

      const apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url.trim())}&hackathon_slug=${vm.hackathonSlug}`;

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
        console.log(vm.form.amount);
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
      if (!vm.terms) {
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
        case '30':
          // rsk
          type = 'rsk_ext';
          break;
        case '50':
          // xinfin
          type = 'xinfin_ext';
          break;
        case '58':
          // polkadot
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
          type = 'qr';
          break;
        case '717171': // other
          type = 'manual';
          break;
        default:
          type = 'web3_modal';
      }

      vm.form.web3_type = type;
      return type;
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
        fundingOrganisation: '',
        eventTag: vm.form.eventTag,
        is_featured: undefined,
        repo_type: 'public',
        featuring_date: 0,
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
        'expires_date': vm.hackathonEndDate,
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
        'coupon_code': '',
        'privacy_preferences': JSON.stringify({
          show_email_publicly: '1'
        }),
        'attached_job_description': '',
        'eventTag': metadata.eventTag,
        'auto_approve_workers': false,
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
    filterOrgSelected: function() {
      if (!this.orgSelected) {
        return;
      }

      return this.sponsors.filter((sponsor) => {
        return sponsor.handle.toLowerCase() === this.orgSelected.toLowerCase();
      });
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
    chainId: async function(val) {
      if (!provider && val === '1') {
        await onConnect();
      }

      if (val === '56') {
        this.getBinanceSelectedAccount();
      }

      this.getTokens();
      await this.checkForm();
    }
  }
});

if (document.getElementById('gc-hackathon-new-bounty')) {
  appFormHackathon = new Vue({
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
        terms: false,
        hackathonSlug: document.hackathon.slug,
        hackathonEndDate: document.hackathon.endDate,
        errors: {},
        sponsors: document.sponsors,
        orgSelected: '',
        // selected: null,
        coinValue: null,
        form: {
          eventTag: document.hackathon.name,
          issueDetails: undefined,
          issueUrl: '',
          githubUsername: document.contxt.github_handle,
          notificationEmail: document.contxt.email,
          fullName: document.contxt.name,
          hours: '24',
          bounty_categories: [],
          project_type: '',
          permission_type: '',
          keywords: [],
          amount: 0.001,
          amountusd: null,
          token: {}
        }
      };
    },
    mounted() {
      this.getTokens();

    }
  });
}
