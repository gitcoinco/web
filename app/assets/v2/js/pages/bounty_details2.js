let bounty = [];
let url = location.href;

Vue.mixin({
  methods: {
    fetchBounty: function() {
      let vm = this;
      let apiUrlBounty = `/actions/api/v0.1/bounty?github_url=${document.issueURL}`;
      const getBounty = fetchData(apiUrlBounty, 'GET');

      $.when(getBounty).then(function(response) {
        vm.bounty = response[0];
        vm.isOwner = vm.checkOwner(response[0].bounty_owner_github_username)
        document.result = response[0];
      })
    },
    checkOwner: function(handle) {
      let vm = this;
      if (document.contxt['github_handle']) {
        return caseInsensitiveCompare(document.contxt['github_handle'], handle);
      } else {
        return false;
      }
    },
    syncGhIssue: function() {
      let vm = this;
      let apiUrlIssueSync = `/sync/get_issue_details?url=${encodeURIComponent(vm.bounty.github_url)}&token=${currentProfile.githubToken}`;
      const getIssueSync = fetchData(apiUrlIssueSync, 'GET');

      $.when(getIssueSync).then(function(response) {
        vm.updateGhIssue(response)
      })
    },
    updateGhIssue: function(response) {
      let vm = this;
      const payload = JSON.stringify({
        issue_description: response.description,
        title: response.title
      });
      let apiUrlUpdateIssue = `/bounty/change/${vm.bounty.pk}`;
      const postUpdateIssue = fetchData(apiUrlUpdateIssue, 'POST', payload);

      $.when(postUpdateIssue).then(function(response) {
        vm.bounty.issue_description = response.description;
        vm.bounty.title = response.title;
        _alert({ message: response.msg }, 'success');
      }).catch(function(response) {
        _alert({ message: response.responseJSON.error }, 'error');
      })
    },
    copyTextToClipboard: function(text) {
      if (!navigator.clipboard) {
        _alert('Could not copy text to clipboard', 'error', 5000)
      } else {
        navigator.clipboard.writeText(text).then(function() {
          _alert('Text copied to clipboard', 'success', 5000)
        }, function(err) {
          _alert('Could not copy text to clipboard', 'error', 5000)
        });
      }
    }
  },
  computed: {

  }
});




if (document.getElementById('gc-bounty-detail')) {
  var appBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-bounty-detail',
    data() {
      return {
        bounty: bounty,
        url: url,
        cb_address: cb_address,
        isOwner: false,
        is_bounties_network: is_bounties_network,
        inputAmount: 0
      }
    },
    mounted() {
      this.fetchBounty();
    }
  });
}
