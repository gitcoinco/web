Vue.filter('moment-fromnow', function(date) {
  moment.defineLocale('en-custom', {
    parentLocale: 'en',
    relativeTime: {
      future: 'in %s',
      past: '%s ',
      s: 'now',
      ss: '%ds',
      m: '1m',
      mm: '%d m',
      h: '1h',
      hh: '%dh',
      d: '1 day',
      dd: '%d days',
      M: '1 month',
      MM: '%d months',
      y: '1 year',
      yy: '%d years'
    }
  });
  return moment.utc(date).fromNow();
});

Vue.filter('moment', function(date) {
  moment.locale('en');
  return moment.utc(date).fromNow();
});

Vue.filter('momentFormat', function(date, format) {
  const _format = !format ? 'LLLL' : format;

  return moment(date).format(_format);
});


Vue.filter('markdownit', function(val) {
  if (!val)
    return '';
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

Vue.filter('truncateHash', function(elem, _number) {
  const number = !_number ? _number = 4 : _number;
  let content = elem.trim();

  return content.substr(0, number + 2) + '\u2026' + content.substr(-number);
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
    new_kudos: gettext('New Kudos')
  };

  return activity_names[activity_type];
});

