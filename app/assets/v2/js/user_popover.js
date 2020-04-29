let popoverData = [];

const renderPopOverData = data => {
  const unique_contributed_to = data.contributed_to ? Array.from(new Set(data.contributed_to)) : [];
  let contributed_to = unique_contributed_to && unique_contributed_to.map((_organization, index) => {
    if (index < 5) {
      return `<img src="/dynamic/avatar/${_organization}" alt="${_organization}"
        class="rounded-circle" width="24" height="24">`;
    }
    return `<span class="m-1">+${data.contributed_to.length - 5}</span>`;
  }).join(' ');

  const bounties = data.related_bounties && data.related_bounties.map(bounty => {
    const title = bounty.title <= 30 ? bounty.title : bounty.title.slice(0, 27) + '...';

    let ratings = [];

    if (bounty.rating && bounty.rating[0] > 0) {
      for (let i = 0; i < 5; i++) {
        ratings.push(`<i class="far fa-star ${ i <= bounty.rating[0] ? 'fas' : ''} "></i>`);
      }
    }

    return `<li>
      <span class="font-weight-semibold bounty-title">${title}</span>
      <span class="bounty-org">by ${bounty.org}</span>
      ${ratings.length > 0 ?
    `<span class="static-stars float-right">
        ${ratings.join(' ')}
      </span>` : ''}
    </li>`;
  }).join(' ');

  return `
    <div class="popover-bounty__content">
      <div class="mb-2">
        <img src="${data.avatar}" width="35" class="rounded-circle">
        <p class="ml-3 d-inline font-body my-auto font-weight-semibold">${data.handle}</p>
        <div class="float-right">
          ${contributed_to.length ? '<span class="my-auto">Contributes to: </span>' + contributed_to : ''}
        </div>
      </div>

      <div class="stats text-center mt-4">
        <div class="stat-card mx-1 mb-2 py-2 px-5 px-sm-3 d-inline-block text-center">
          <h2 class="font-title font-weight-bold mb-0">
            ${data.stats.position == 0 ? '-' : '#' + data.stats.position}
          </h2>
          <p class="font-body mb-0">contributor</p>
        </div>
        <div class="stat-card mx-1 mb-2 py-2 px-5 px-sm-3 d-inline-block text-center">
          <h2 class="font-title font-weight-bold mb-0">
            ${data.stats.success_rate ? Math.round(data.stats.success_rate) : 0} %
          </h2>
          <p class="font-body mb-0">success rate</p>
        </div>
        <div class="stat-card mx-1 mb-2 py-2 px-5 px-sm-3 d-inline-block text-center">
          <h2 class="font-title font-weight-bold mb-0">
            ${data.stats.earnings ? Number(data.stats.earnings).toFixed(4) : 0} ETH
          </h2>
          <p class="font-body mb-0">
            collected from
            <span class="font-weight-bold">${data.stats.completed_bounties}</span> bounties
          </p>
        </div>
      </div>

    ${data.related_bounties.length == 0 ?
    `<p class="font-body mt-3 summary">
        No bounties completed related to <span class="font-italic">${data.keywords || 'bounty'}</span>
      </p>`
    :
    `<p class="font-body mt-3 summary">
        Bounties completed related to <span class="font-italic">${data.keywords || 'bounty'}:</span>
      </p>
      <ul class="related-bounties font-body pl-0">
        ${bounties}
      </ul>`
}

    </div>
  `;
};
let controller = null;

function openContributorPopOver(contributor, element) {
  const keywords = document.result.keywords || '';
  const contributorURL = `/api/v0.1/profile/${contributor}?keywords=${keywords}`;

  if (popoverData.filter(index => index[contributor]).length === 0) {
    if (controller) {
      controller.abort();
    }
    controller = new AbortController();
    const signal = controller.signal;

    userRequest = fetch(contributorURL, { method: 'GET', signal })
      .then(response => response.json())
      .then(response => {
        popoverData.push({ [contributor]: response });
        controller = null;
        element.popover({
          placement: 'auto',
          // container: element,
          trigger: 'manual',
          delay: { 'show': 200, 'hide': 500 },
          template: `
            <div class="popover popover-bounty" role="tooltip">
              <div class="arrow"></div>
              <h3 class="popover-header"></h3>
              <div class="popover-body"></div>
            </div>`,
          content: renderPopOverData(response),
          html: true
        }).on('mouseenter', function() {
          var _this = this;

          $(this).popover('show');
          $('.popover').on('mouseleave', function() {
            $(_this).popover('hide');
          });
        }).on('mouseleave', function() {
          var _this = this;

          setTimeout(function() {
            if (!$('.popover:hover').length) {
              $(_this).popover('hide');
            }
          }, 100);
        });
        $(element).popover('show');
      })
      .catch(err => {
        return console.warn({ message: err });
      });
  } else {
    element.popover({
      placement: 'auto',
      // container: element,
      trigger: 'manual',
      delay: { 'show': 200, 'hide': 500 },
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
    }).on('mouseenter', function() {
      var _this = this;

      $(this).popover('show');
      $('.popover').on('mouseleave', function() {
        $(_this).popover('hide');
      });
    }).on('mouseleave', function() {
      var _this = this;

      setTimeout(function() {
        if (!$('.popover:hover').length) {
          $(_this).popover('hide');
        }
      }, 100);
    });
    $(element).popover('show');
  }
}
