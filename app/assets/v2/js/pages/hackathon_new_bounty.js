let appFormHackathon;
// const hackathonSlug = document.hackathon.slug;
const sponsors = document.sponsors;

window.addEventListener('dataWalletReady', function(e) {
  appFormHackathon.network = networkName;
}, false);

Vue.component('v-select', VueSelect.VueSelect);
Vue.mixin({
  methods: {
    getIssueDetails: function(url) {
      let vm = this;

      if (!url) {
        vm.errorIssueDetails = undefined;
        vm.form.issueDetails = null;
        return vm.form.issueDetails;
      }

      if (url.indexOf('github.com/') < 0) {
        vm.form.issueDetails = null;
        vm.errorIssueDetails = 'Please paste a github issue url';
        return;
      }

      let ghIssueUrl = new URL(url);

      vm.orgSelected = '';

      const apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url)}&hackathon_slug=${vm.hackathonSlug}`;

      vm.errorIssueDetails = undefined;
      vm.form.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        vm.orgSelected = ghIssueUrl.pathname.split('/')[1];

        vm.form.issueDetails = response;
        vm.errorIssueDetails = undefined;
        // if (response[0]) {
        // } else {
        //   vm.issueDetails = null;
        //   vm.errorIssueDetails = 'This issue wasn\'t bountied yet.';
        // }
      }).catch((err) => {
        console.log(err);
        vm.errorIssueDetails = err.responseJSON.message;
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

      $.when(getAmountData).then((response) => {
        vm.coinValue = response.usdt;
        vm.calcValues('usd');

      }).catch((err) => {
        console.log(err);
        // vm.errorIssueDetails = err.responseJSON.message;
      });
    },
    calcValues: function(direction) {
      let vm = this;

      if (direction == 'usd') {
        let usdValue = vm.form.amount * vm.coinValue;

        vm.form.amountusd = Number(usdValue.toFixed(2));
        console.log(vm.form.amountusd);
      } else {
        vm.form.amount = Number(vm.form.amountusd * 1 / vm.coinValue).toFixed(4);
        console.log(vm.form.amount);
      }

    },
    addKeyword: function(item) {
      let vm = this;

      vm.form.keywords.push(item);
    },
    checkForm: function(e) {
      let vm = this;

      if (vm.form.bounty_categories.length < 1) {
        vm.errors.push('Select at least one category');
        e.preventDefault();
      } else {
        return;
      }
    },
    web3Type() {
      let vm = this;
      let type;

      switch (vm.chainId) {
        case '1':
          // ethereum
          type = 'bounties_network';
          break;
        case '666':
          // paypal
          type = 'fiat';
          break;
        case '61':
          // ethereum classic
          type = 'qr';
          break;
        case '102':
          // zilliqa
          type = 'qr';
          break;
        default:
          type = 'bounties_network';
      }

      vm.form.web3_type = type;
    },
    submitForm: function() {
      let vm = this;

      const metadata = {
        issueTitle: vm.form.issueDetails.title,
        issueDescription: vm.form.issueDetails.description,
        issueKeywords: vm.form.keywords,
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
        bounty_categories: vm.form.bounty_categories,
        activity: '',
        chain_id: vm.chainId
      };

      const params = {
        'title': metadata.issueTitle,
        'amount': vm.form.amount,
        'value_in_token': vm.form.amount * 10 ** vm.form.token.decimals,
        'token_name': metadata.tokenName,
        'token_address': vm.form.address,
        'bounty_type': metadata.bountyType,
        'project_length': metadata.projectLength,
        'estimated_hours': metadata.estimatedHours,
        'experience_level': metadata.experienceLevel,
        'github_url': vm.form.issueURL,
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
          _alert('Unable to create a bounty. Please try again later', 'error');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        }

      }).catch((err) => {
        console.log(err);
        _alert('Unable to create a bounty. Please try again later', 'error');
        // vm.errorIssueDetails = err.responseJSON.message;
      });

    }
    // blockchainSend: function() {

    // }
  },
  computed: {
    sortByPriority: function() {
      // console.log(elem)
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
      // vm.chainId = form.bounty_chain;
      if (vm.chainId == '') {
        result = vm.filterByNetwork;
      } else {
        result = vm.filterByNetwork.filter((item)=>{
          console.log(item.chainId, vm.chainId);

          return String(item.chainId) === vm.chainId;
        });
      }
      vm.form.token = result[0];
      return result;
    }
  }
});

if (document.getElementById('gc-hackathon-new-bounty')) {
  // var vueSelect = import('vue-select');
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
        hackathonSlug: document.hackathon.slug,
        hackathonEndDate: document.hackathon.endDate,
        errorIssueDetails: undefined,
        errors: [],
        sponsors: sponsors,
        orgSelected: '',
        selected: null,
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
