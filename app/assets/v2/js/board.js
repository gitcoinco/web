

Vue.mixin({
  methods: {
    fetchBounties: function(newPage) {
      let vm = this;
      let apiUrlbounties = `api/v0.1/get_bounties/`;
      var getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.profile = response.profile;
        vm.bounties = response.bounties;
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
      notifications: notifications
    },
    mounted() {
      this.fetchBounties();
    }

  });
}
