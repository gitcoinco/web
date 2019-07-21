
Vue.mixin({
  methods: {
    fetchBounties: function(type) {
      let vm = this;
      let apiUrlbounties = `/funder_dashboard/${type}/`;
      let getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.$set(vm.bounties, type, response);
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
        // vm.$set(vm.openBounties[key],'contributors', response.profiles)

      });
    },
    isExpanded(key) {
      return this.expandedGroup.indexOf(key) !== -1;
    },
    toggleCollapse(key) {
      if (this.isExpanded(key)) {
        this.expandedGroup.splice(this.expandedGroup.indexOf(key), 1);
      } else {
        this.expandedGroup.push(key);
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
    stopWork(key, bountyPk, profileId) {
      let vm = this;
      let url = `/actions/bounty/${bountyPk}/interest/${profileId}/uninterested/`;
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
    }
  }
});

if (document.getElementById('gc-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-board',
    data: {
      bounties: {},
      openBounties: [],
      submittedBounties: [],
      expiredBounties: [],
      expandedGroup: [],
      contributors: [],
      disabledBtn: false
    },
    mounted() {
      this.fetchBounties('open');
      this.fetchBounties('submitted');
      this.fetchBounties('expired');
    }

  });
}

Vue.filter('pluralize', (word, amount, singular, plural) => {
  plural = plural || 's';
  singular = singular || '';
  return amount > 1 ? `${word + plural}` : `${word + singular}`;
});

Vue.filter('moment', (date) => {
  moment.locale('en');
  return moment.utc(date).fromNow();
});
