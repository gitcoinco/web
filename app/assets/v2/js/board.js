

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
    },
    isExpanded(key) {
    	return this.expandedGroup.indexOf(key) !== -1;
    },
    toggleExpansion(key) {
    	if (this.isExpanded(key))
        this.expandedGroup.splice(this.expandedGroup.indexOf(key), 1);
      else
        this.expandedGroup.push(key);
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
      expandedGroup: []
    },
    mounted() {
      this.fetchBounties();
    }

  });
}
