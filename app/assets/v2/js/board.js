let contributorBounties = {};
let pTokens = {};
let bounties = {};
let authProfile = document.contxt.profile_id;
let skills = document.skills;

const PTokenFactory = {
  abi: [
    {
      'anonymous': false,
      'inputs': [
        {
          'indexed': false,
          'internalType': 'contract PToken',
          'name': 'token',
          'type': 'address'
        }
      ],
      'name': 'NewPToken',
      'type': 'event'
    },
    {
      'inputs': [
        {
          'internalType': 'string',
          'name': '_name',
          'type': 'string'
        },
        {
          'internalType': 'string',
          'name': '_symbol',
          'type': 'string'
        },
        {
          'internalType': 'uint256',
          'name': '_cost',
          'type': 'uint256'
        },
        {
          'internalType': 'uint256',
          'name': '_supply',
          'type': 'uint256'
        }
      ],
      'name': 'createPToken',
      'outputs': [],
      'stateMutability': 'nonpayable',
      'type': 'function'
    }
  ]
};

Vue.mixin({
  methods: {
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
      const apiUrlbounties = `/api/v0.1/bounties/slim/?network=${network}&idx_status=open&applicants=ALL&keywords=${vm.skills}&order_by=-web3_created&offset=0&limit=10`;

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
        _alert({ message: gettext(msg) }, 'error');
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

          _alert({ message: gettext(msg) }, 'error');
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

          _alert({ message: gettext(msg) }, 'error');
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
      if (!Object.keys(vm.pTokens).length && persona === 'personal-tokens') {
        vm.fetchTokens('open');
        vm.fetchTokens('accepted');
        vm.fetchTokens('completed');
        vm.fetchTokens('denied');
      }
    },
    tabOnLoad() {
      let vm = this;

      if (document.contxt.persona_is_hunter) {
        vm.checkData('contributor');
        $('#contributor-tab').tab('show');
      } else {
        vm.checkData('funder');
        $('#funder-tab').tab('show');
      }
    },
    redirect(url) {
      document.location.href = url;
    },
    async createPToken() {
      try {
        // TODO: Show loading while deploying
        this.newPToken.deploying = true;
        await this.deployToken();
        this.newPToken.deploying = false;
      } catch (error) {
        console.log(error);
      }
      // this.saveToDB();
    },
    async deployToken() {
      [user] = await web3.eth.getAccounts();
      // TODO: This is a deterministic localhost address. Should be an env variable for rinkeby/mainnet.
      const factoryAddress = '0x7bE324A085389c82202BEb90D979d097C5b3f2E8';
      const factory = await new web3.eth.Contract(PTokenFactory.abi, factoryAddress);

      await factory.methods.createPToken(
        this.newPToken.name,
        this.newPToken.symbol,
        this.newPToken.price,
        this.newPToken.supply
      ).send({
        from: user
      });
    }
  }
});


if (document.getElementById('gc-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-board',
    data: {
      network: network,
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
    mounted() {
      this.tabOnLoad();
    }
  });
}

Vue.filter('pluralize', (word, amount, singular, plural) => {
  plural = plural || 's';
  singular = singular || '';
  return amount !== 1 ? `${word + plural}` : `${word + singular}`;
});

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
