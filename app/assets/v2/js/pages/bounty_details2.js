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
    }
  },
  computed: {

  }
});

Vue.filter('myfilter', function(val) {
  if (!val) return '';
  const _markdown = new markdownit({
    linkify: true,
    highlight: function(str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return `<pre class="hljs"><code>${hljs.highlight(lang, str, true).value}</code></pre>`;
        } catch (__) {}
      }
      return `<pre class="hljs"><code>${sanitize(_markdown.utils.escapeHtml(str))}</code></pre>`;
    }
  });

  _markdown.renderer.rules.table_open = function() {
    return '<table class="table">';
  };
  ui_body = sanitize(_markdown.render(val));
  return ui_body;
});


if (document.getElementById('gc-bounty-detail')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-bounty-detail',
    data: {
      bounty: bounty,
      url: url,
      cb_address: cb_address,
      isOwner: false
    },
    mounted() {
      this.fetchBounty();
    }
  });
}
