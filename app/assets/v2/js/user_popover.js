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
    org =>
      `<img src="/dynamic/avatar/${org}" alt="${org}" class="rounded-circle" width="24" height="24">`
  )}
              </div>
              <span class="earned">~ ${
  json.profile.total_earned
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
        return _alert({ message: err }, 'error');
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
  if (status === 'worker_applied') {
    return 'Work Applied';
  } else if (status === 'start_work') {
    return 'Work Started';
  } else if (status === 'worker_approved') {
    return 'Worker Approved';
  } else if (status === 'stop_work') {
    return 'Stopped Work';
  } else if (status === 'work_submitted') {
    return 'Submitted Work';
  }
  return status;
};
