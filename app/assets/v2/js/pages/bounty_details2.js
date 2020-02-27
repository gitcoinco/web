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
    }
  },
  computed: {

  }
});

Vue.filter('markdownit', function(val) {
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

Vue.filter('stringReplace', function(activity_type) {
  const activity_names = {
    new_bounty: gettext('Bounty Created'),
    start_work: gettext('Work Started'),
    stop_work: gettext('Work Stopped'),
    work_submitted: gettext('Work Submitted'),
    work_done: gettext('Work Done'),
    worker_approved: gettext('Approved'),
    worker_rejected: gettext('Rejected Contributor'),
    worker_applied: gettext('Contributor Applied'),
    increased_bounty: gettext('Increased Funding'),
    killed_bounty: gettext('Canceled Bounty'), // All other sections become empty ?
    new_crowdfund: gettext('Added new Crowdfund Contribution'),
    new_tip: gettext('Tip Sent'),
    receive_tip: gettext('Tip Received'),
    bounty_changed: gettext('Bounty Details Updated'),
    extend_expiration: gettext('Extended Bounty Expiration'),
    bounty_abandonment_escalation_to_mods: gettext('Escalated for Abandonment of Bounty'),
    bounty_abandonment_warning: gettext('Warned for Abandonment of Bounty'),
    bounty_removed_slashed_by_staff: gettext('Dinged and Removed from Bounty by Staff'),
    bounty_removed_by_staff: gettext('Removed from Bounty by Staff'),
    bounty_removed_by_funder: gettext('Removed from Bounty by Funder'),
  };
  return activity_names[activity_type];
})


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
