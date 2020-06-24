window.addEventListener('dataWalletReady', function(e) {
  app.network = networkName;
}, false);

const hackathon_slug = document.hackathon_slug;
const sponsors = document.sponsors;

Vue.component('v-select', VueSelect.VueSelect);
Vue.mixin({
  methods: {
    getIssueDetails: function(url) {
      let vm = this;

      if (!url) {
        vm.errorIssueDetails = undefined;
        vm.issueDetails = null;
        return vm.issueDetails;
      }

      if (url.indexOf('github.com/') < 0) {
        vm.issueDetails = null;
        vm.errorIssueDetails = 'Please paste a github issue url';
        return;
      }

      let ghIssueUrl = new URL(url);

      vm.orgSelected = '';

      const apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url)}&hackathon_slug=${vm.hackathon_slug}`;

      vm.errorIssueDetails = undefined;
      vm.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        vm.orgSelected = ghIssueUrl.pathname.split('/')[1];

        vm.issueDetails = response;
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
    submitForm: function() {
      let vm = this;

      if (network === 'mainnnet') {
        // vm.blockchainSend(form)
        // vm.sendData(form)

      } else if (network === 'custom') {
        // vm.sendData(form)
      }
    },
    sendData: function() {
      let vm = this;

      const params = {
        'title': metadata.issueTitle,
        'amount': data.amount,
        'value_in_token': data.amount * 10 ** token.decimals,
        'token_name': metadata.tokenName,
        'token_address': tokenAddress,
        'bounty_type': metadata.bountyType,
        'project_length': metadata.projectLength,
        'estimated_hours': metadata.estimatedHours,
        'experience_level': metadata.experienceLevel,
        'github_url': data.issueURL,
        'bounty_owner_email': metadata.notificationEmail,
        'bounty_owner_github_username': metadata.githubUsername,
        'bounty_owner_name': metadata.fullName, // ETC-TODO REMOVE ?
        'bounty_reserved_for': metadata.reservedFor,
        'release_to_public': metadata.releaseAfter,
        'expires_date': expiresDate,
        'metadata': JSON.stringify(metadata),
        'raw_data': {}, // ETC-TODO REMOVE ?
        'network': network,
        'issue_description': metadata.issueDescription,
        'funding_organisation': metadata.fundingOrganisation,
        'balance': data.amount * 10 ** token.decimals, // ETC-TODO REMOVE ?
        'project_type': data.project_type,
        'permission_type': data.permission_type,
        'bounty_categories': metadata.bounty_categories,
        'repo_type': data.repo_type,
        'is_featured': is_featured,
        'featuring_date': metadata.featuring_date,
        'fee_amount': fee_amount,
        'fee_tx_id': fee_tx_id,
        'coupon_code': coupon_code,
        'privacy_preferences': JSON.stringify(privacy_preferences),
        'attached_job_description': hiring.jobDescription,
        'eventTag': metadata.eventTag,
        'auto_approve_workers': data.auto_approve_workers ? 'True' : 'False',
        'web3_type': web3_type,
        'activity': data.activity,
        'bounty_owner_address': data.funderAddress
      };

      // api post method
      const url  = '/api/v1/bounty/create';

      $.post(url, params, function(response) {
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
      });

    },
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

      vm.form.token = {}
      // vm.chainId = form.bounty_chain;
      if (vm.chainId == '') {
        result = vm.filterByNetwork;
      } else {
        result = vm.filterByNetwork.filter((item)=>{
          console.log(item.chainId, vm.chainId)

          return String(item.chainId) === vm.chainId;
        });
      }
      vm.form.token = result[0];
      return result
    }
  }
});

if (document.getElementById('gc-hackathon-new-bounty')) {
  // var vueSelect = import('vue-select');
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-hackathon-new-bounty',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        tokens: [],
        network: '',
        chainId: '',
        hackathon_slug: hackathon_slug,
        issueDetails: undefined,
        errorIssueDetails: undefined,
        errors: [],
        sponsors: sponsors,
        orgSelected: '',
        selected: null,
        coinValue: null,
        form: {
          gitcoinIssueUrl: '',
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
