let popoverData = [];

const renderPopOverData = data => {
  console.log(data)
  let contributed_to = data.contributed_to.map((_organization, index) => {
    if (index < 3) {
      return `<img src="/dynamic/avatar/${_organization}" alt="${_organization}"
        class="rounded-circle" width="24" height="24">`;
    }
    return `<span class="m-1">+${data.contributed_to.length - 3}</span>`;
  }).join(' ');

  return `
    <div class="popover-bounty__content">
      <div class="mb-2">
        <img src="${data.avatar}" width="35" class="rounded-circle">
        <p class="ml-3 d-inline font-body my-auto font-weight-semibold">${data.handle}</p>
        ${contributed_to.length ? '<span class="my-auto">Contributes to: </span>' + contributed_to : ''}
      </div>

      <div class="stats">
        <div class="stat-card d-inline">
          <h2>${data.stats.position}</h2>
          <p>contributor</p>
        </div>
        <div class="stat-card d-inline">
          <h2>${data.stats.success_rate}</h2>
          <p>success rate</p>
        </div>
        <div class="stat-card d-inline">
          <h2>${data.stats.earnings ? Number(data.stats.earnings).toFixed(4) : 0} ETH</h2>
          <p>collected from ${data.stats.completed_bounties} bounties</p>
        </div>
      </div>

      <p>Bounties completed related to ${data.keywords.slice(0, 3).toString()}</p>
      ${data.related_bounties ?
    '<ul><li>// TODO: LOOP THROUGH TITLE</li></ul>'
    :
    '<p>None</p>'
}

    </div>
  `;
};

function openContributorPopOver(contributor, element) {
  const keywords = document.result.keywords;
  const contributorURL = `/api/v0.1/profile/${contributor}?keywords=${keywords}`;

  if (popoverData.filter(index => index[contributor]).length === 0) {
    fetch(contributorURL, { method: 'GET' })
      .then(response => response.json())
      .then(response => {
        element.popover({
          placement: 'auto',
          trigger: 'hover',
          template: `
            <div class="popover popover-bounty" role="tooltip">
              <div class="arrow"></div>
              <h3 class="popover-header"></h3>
              <div class="popover-body"></div>
            </div>`,
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
      template: `
        <div class="popover popover-bounty" role="tooltip">
          <div class="arrow"></div>
          <h3 class="popover-header"></h3>
          <div class="popover-body"></div>
        </div>`,
      content: renderPopOverData(
        popoverData.filter(item => item[contributor])[0][contributor]
      ),
      html: true
    });
    $(element).popover('show');
  }
}
