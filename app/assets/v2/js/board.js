let contributorBounties = {};
let bounties = {};
let authProfile = document.contxt.profile_id;

Vue.mixin({
  methods: {
    fetchBounties: function(type) {
      let vm = this;
      let apiUrlbounties = `/funder_dashboard/${type}/`;
      let getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.$set(vm.bounties, type, response);
        vm.isLoading[type] = false;
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
      });
    },
    fetchContributorBounties: function(type) {
      let vm = this;
      let apiUrlbounties = `/contributor_dashboard/${type}/`;
      let getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.$set(vm.contributorBounties, type, response);
        vm.isLoading[type] = false;

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
    checkData(persona) {
      let vm = this;

      if (!Object.keys(vm.bounties).length && persona === 'funder') {
        vm.fetchBounties('open');
        vm.fetchBounties('submitted');
        vm.fetchBounties('expired');
      }

      if (!Object.keys(vm.contributorBounties).length && persona === 'contributor') {
        vm.fetchContributorBounties('work_in_progress');
        vm.fetchContributorBounties('work_submitted');
        vm.fetchContributorBounties('interested');
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
    }
  }
});

if (document.getElementById('gc-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-board',
    data: {
      bounties: bounties,
      openBounties: [],
      submittedBounties: [],
      expiredBounties: [],
      contributors: [],
      contributorBounties: contributorBounties,
      expandedGroup: {'submitted': [], 'open': []},
      disabledBtn: false,
      authProfile: authProfile,
      isLoading: {
        'open': true,
        'openContrib': true,
        'submitted': true,
        'submittedContrib': true,
        'expired': true,
        'work_in_progress': true,
        'interested': true,
        'work_submitted': true
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
