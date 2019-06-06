Vue.mixin({
  methods: {
    fetchBounties: function(newPage) {
      let vm = this;
      let apiUrlbounties = `api/v0.1/get_bounties/`;
      var getbounties = fetchData (apiUrlbounties, 'GET');

      $.when(getbounties).then(function(response) {
        vm.profile = response.profile;
      })
    }
  }
});

if (document.getElementById('gc-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-board',
    data: {
      profile: []
    },
    mounted() {
      this.fetchBounties();
    }

  });
}
