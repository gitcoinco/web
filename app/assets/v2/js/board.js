var interested =[{"profile":{"id":13,"handle":"octavioamu","github_url":"https://github.com/octavioamu","avatar_url":"/media/avatars/72f4f6d365732c50762730b1bc630379/octavioamu.png","keywords":["CSS","JavaScript","HTML","PHP"],"url":"/profile/octavioamu","position":0,"organizations":{},"total_earned":0, "work_completed":3},
"avg_rating": {"overall": 2, "code_quality_rating": 0, "communication_rating": 0, "recommendation_rating": 0, "satisfaction_rating": 0, "speed_rating": 0, "total_rating": 0},"created":"2019-07-10T15:09:39.148065Z","pending":false,"signed_nda":null},
{"profile":{"id":13,"handle":"oktopustester","github_url":"https://github.com/oktopustester","avatar_url":"/media/avatars/d7620227c9c48a33f697d7e875013d7e/oktopustester.png","keywords":["CSS","JavaScript","HTML","PHP"],"url":"/profile/oktopustester","position":0,"organizations":{},"total_earned":0, "work_completed":1},
"avg_rating": {"overall": 3, "code_quality_rating": 0, "communication_rating": 0, "recommendation_rating": 0, "satisfaction_rating": 0, "speed_rating": 0, "total_rating": 0}, "created":"2019-07-10T15:09:39.148065Z","pending":false,"signed_nda":null}]

Vue.mixin({
  methods: {
    fetchBounties: function(newPage) {
      let vm = this;
      let apiUrlbounties = `api/v0.1/get_bounties/`;
      let getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.profile = response.profile;
        vm.bounties = response.bounties;
      })
    },
    isExpanded(key) {
    	return this.expandedGroup.indexOf(key) !== -1;
    },
    toggleCollapse(key) {
    	if (this.isExpanded(key))
        this.expandedGroup.splice(this.expandedGroup.indexOf(key), 1);
      else
        this.expandedGroup.push(key);
    },
    startWork(key, bountyPk, profileId) {
      let vm = this;
      vm.disabledBtn = key
      let url = `/actions/bounty/${bountyPk}/interest/${profileId}/interested/`;
      let postStartpWork = fetchData (url, 'POST');
      console.log(key)

      $.when(postStartpWork).then(response => {
        vm.contributors.splice(key, 1);
        vm.disabledBtn = '';
        _alert({ message: gettext('Contributor removed from bounty.') }, 'success');
      }, error => {
        vm.disabledBtn = '';
        let msg = error.responseJSON.error || 'got an error. please try again, or contact support@gitcoin.co';
        console.log(error.responseJSON.error)
        _alert({ message: gettext(msg) }, 'error');
      })
    },
    stopWork(key, bountyPk, profileId) {
      let vm = this;
      vm.disabledBtn = key
      let url = `/actions/bounty/${bountyPk}/interest/${profileId}/uninterested/`;
      let postStartpWork = fetchData (url, 'POST');
      console.log(key)

      $.when(postStartpWork).then(response => {
        vm.contributors.splice(key, 1);
        vm.disabledBtn = '';
        _alert({ message: gettext('Contributor removed from bounty.') }, 'success');
      }, error => {
        vm.disabledBtn = '';
        let msg = error.responseJSON.error || 'got an error. please try again, or contact support@gitcoin.co';
        console.log(error.responseJSON.error)
        _alert({ message: gettext(msg) }, 'error');
      })
    }
  }
});

if (document.getElementById('gc-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-board',
    data: {
      profile: [],
      bounties: [],
      expandedGroup: [],
      contributors: interested,
      disabledBtn: false
    },
    mounted() {
      this.fetchBounties();
    }

  });
}




