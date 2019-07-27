let popoverData = [];

const renderPopOverData = json => {
  return `
            <div class="popover-bounty__content">
              <div class="d-flex justify-content-between mb-2">
                <h2 class="title font-subheader font-weight-bold username">${
  json.profile.handle
}</h2>
                <span class="text-muted specialty pt-2">Specialty: ${json.profile.keywords
    .slice(0, 3)
    .toString()}</span>
                                  ${Object.keys(json.profile.organizations).map(
    (org, index) => {
      if (index < 3) {
        `<img src="/dynamic/avatar/${org}" alt="${org}" class="rounded-circle" width="24" height="24">`;
      } else {
        `<img class="rounded-circle m-1" width="24" height="24" title=${Object.keys(json.profile.organizations.length)} times" src=""/>`;
      }
    }
  )}
              </div>
              <span class="earned">~ ${
  Number(json.profile.total_earned).toFixed(4)
} ETH earned</span>
              <div class="statistics d-flex justify-content-between mt-2">
                <div class="popover_card text-center mr-4 pt-2">
                  <span class="contributor-position font-weight-semibold">#${
  json.profile.position
}</span>
                  <p class="mt-2">Gitcoin Contributor</p>
                </div>
                <div class="contributions d-flex justify-content-between">
                  <div class="popover_card text-center mr-2 pt-2">
                    <span class="completed-bounties font-weight-semibold">${
  json.statistics.work_completed
}</span>
                    <p class="mt-2">Bounties Completed</p>
                  </div>
                  <div class="popover_card text-center mr-2 pt-2">
                    <span class="in-progress text-center font-weight-semibold">${
  json.statistics.work_in_progress
}</span>
                    <p class="mt-2">Bounties In Progress</p>
                  </div>
                  <div class="popover_card text-center mr-2 pt-2">
                    <span class="abandoned-bounties font-weight-semibold">${
  json.statistics.work_abandoned
}</span>
                    <p class="mt-2">Bounties Abandoned</p>
                  </div>
                  <div class="popover_card text-center mr-2 pt-2">
                    <span class="removed-bounties font-weight-semibold">${
  json.statistics.work_removed
}</span>
                    <p class="mt-2">Bounties Removed</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="popover-bounty__footer">
              <div class="d-flex justify-content-between">
                <span class="title text-muted">Latest Activity
                  <span class="current_status font-weight-semibold">${currentStatus(
    json.recent_activity.activity_type
  )}</span>
                </span>
                <span class="text-muted time-ago">${moment(
    json.recent_activity.created,
    'YYYYMMDD'
  ).fromNow()}</span>
              </div>
              <p class="text-muted pt-2 activity-title">${
  json.recent_activity.activity_metadata.title
}</p>
            </div>`;
};

const openContributorPopOver = (contributor, element) => {
  let contributorURL = `/api/v0.1/profile/${contributor}`;

  if (popoverData.filter(index => index[contributor]).length === 0) {
    fetch(contributorURL, { method: 'GET' })
      .then(response => response.json())
      .then(response => {
        element.popover({
          placement: 'auto',
          trigger: 'hover',
          template:
            '<div class="popover popover-bounty" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>',
          content: renderPopOverData(response),
          html: true
        });
        $(element).popover('show');
        popoverData.push({ [contributor]: response });
      })
      .catch(err => {
        return console.error({ message: err }, 'error');
      });
  } else {
    element.popover({
      placement: 'auto',
      trigger: 'hover',
      template:
        '<div class="popover popover-bounty" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>',
      content: renderPopOverData(
        popoverData.filter(item => item[contributor])[0][contributor]
      ),
      html: true
    });
    $(element).popover('show');
  }
};

const currentStatus = status => {
  const activity_names = {
    new_bounty: gettext('New Bounty'),
    start_work: gettext('Work Started'),
    stop_work: gettext('Work Stopped'),
    work_submitted: gettext('Work Submitted'),
    work_done: gettext('Work Done'),
    worker_approved: gettext('Worker Approved'),
    worker_rejected: gettext('Worker Rejected'),
    worker_applied: gettext('Worker Applied'),
    increased_bounty: gettext('Increased Funding'),
    killed_bounty: gettext('Canceled Bounty'),
    new_crowdfund: gettext('New Crowdfund Contribution'),
    new_tip: gettext('New Tip'),
    receive_tip: gettext('Tip Received'),
    bounty_abandonment_escalation_to_mods: gettext(
      'Escalated for Abandonment of Bounty'
    ),
    bounty_abandonment_warning: gettext('Warned for Abandonment of Bounty'),
    bounty_removed_slashed_by_staff: gettext(
      'Dinged and Removed from Bounty by Staff'
    ),
    bounty_removed_by_staff: gettext('Removed from Bounty by Staff'),
    bounty_removed_by_funder: gettext('Removed from Bounty by Funder'),
    bounty_changed: gettext('Bounty Details Changed'),
    extend_expiration: gettext('Extended Bounty Expiration')
  };

  return activity_names[status] || 'Unknown activity ';
};
