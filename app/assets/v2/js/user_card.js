$('body').on('mouseover', '[data-usercard]', function(e) {
  openContributorPopOver($(this).data('usercard'), $(this));
}).on('mouseleave', '[data-usercard]', function() {
  var elem = this;

  setTimeout(function() {
    if (!$('.popover-user-card:hover').length) {
      $(elem).popover('hide');
    }
  }, 100);

  $('.popover-user-card').on('mouseleave', function() {
    $(elem).popover('hide');
  });
});

$('body').on('show.bs.popover', '[data-usercard]', function() {
  $('body [data-usercard]').not(this).popover('hide');
  setTimeout(function() {
    if (!$('.popover-user-card:hover').length) {
      $(this).popover('hide');
    }
  }, 100);
});

let popoverData = [];
let controller = null;

const renderPopOverData = function(data) {
  const unique_orgs = data && data.profile && data.profile.orgs ? Array.from(new Set(data.profile.orgs)) : [];
  let orgs = unique_orgs && unique_orgs.map((_organization, index) => {
    if (index < 5) {
      return `<a href="/${_organization}" class="link-current" data-toggle="tooltip" data-container=".popover-user-card" data-original-title="${_organization}">
        <img src="/dynamic/avatar/${_organization}" alt="${_organization}" class="rounded-circle border" width="24" height="24">
        </a>`;
    } else if (index < 6) {
      return `<span class="m-1">+${unique_orgs.length - 5}</span>`;
    }
  }).join(' ');

  function percentCalc(value, total) {
    let result = value * 100 / total;

    return isNaN(result) ? 0 : result;
  }

  let dashoffset = 25;

  function calcDashoffset(thispercentage) {
    let oldOffset = dashoffset;

    accumulate += thispercentage;
    dashoffset = (100 - accumulate) + 25;
    return oldOffset;
  }

  function objSetup(sent, received, total, color, colorlight, stringsOverwrite) {
    let prodTotal = sent + received;

    return {
      'percent': percentCalc(prodTotal, total),
      'percentsent': percentCalc(sent, prodTotal),
      'amountsent': sent,
      'percentreceived': percentCalc(received, prodTotal),
      'amountreceived': received,
      'color': color,
      'colorlight': colorlight,
      'dashoffset': calcDashoffset(percentCalc(prodTotal, total)),
      'strings': stringsOverwrite
    };
  }
  let tips_total = data.profile_dict.total_tips_sent + data.profile_dict.total_tips_received;
  let bounties_total = data.profile_dict.funded_bounties_count + data.profile_dict.count_bounties_completed;
  let grants_total = data.profile_dict.total_grant_created + data.profile_dict.total_grant_contributions;
  let total = tips_total + bounties_total + grants_total;
  let accumulate = 0;
  let tips_total_percent = objSetup(
    data.profile_dict.total_tips_sent,
    data.profile_dict.total_tips_received,
    total,
    '#89CD69',
    '#BFE1AF',
    {'type': 'Tips', 'sent': 'Sent', 'received': 'Received'}
  );
  let token_total_percent = objSetup(
    data.profile.purchased_count || 0,
    data.profile.redeemed_count || 0,
    total,
    '#D8C667',
    '#FFED90',
    {'type': 'Token', 'sent': 'Purch', 'received': 'Redeem'}
  );
  let bounties_total_percent = objSetup(
    data.profile_dict.funded_bounties_count,
    data.profile_dict.count_bounties_completed,
    total,
    '#8E98FF',
    '#ADB4FF',
    {'type': 'Bounties', 'sent': 'Created', 'received': 'Worked'}
  );
  let grants_total_percent = objSetup(
    data.profile_dict.total_grant_created,
    data.profile_dict.total_grant_contributions,
    total,
    '#FF83FA',
    '#FFB2FC',
    {'type': 'Grants', 'sent': 'Fund', 'received': 'Contrib'}
  );

  let mount_graph = [ tips_total_percent, bounties_total_percent, grants_total_percent ];

  if (data.profile.has_ptoken) {
    mount_graph.push(token_total_percent);
  }


  let graphs = mount_graph.map((graph) => {
    return `<circle class="donut-segment" cx="50%" cy="50%" r="38%" fill="transparent" stroke="${graph.color}" stroke-width="8%" stroke-dasharray="${graph.percent} ${100 - graph.percent}" stroke-dashoffset="${graph.dashoffset}"></circle>`;
  }).join(' ');

  const renderAvatarData = function() {
    return `
    <svg width="100%" height="100%" viewBox="0 0 42 42" class="user-card_donut-chart">
      <circle stroke-width="8%" stroke="#d2d3d4" fill="transparent" r="38%" cy="50%" cx="50%" class="donut-ring"></circle>
      ${graphs}
      <defs>
        <clipPath id="myCircle">
          <circle cx="50%" cy="50%" r="34%" fill="#FFFFFF" />
        </clipPath>
      </defs>

      <g class="chart-text">
      <image xlink:href="${data.profile.avatar_url}" x="3" y="3" height="86%" width="86%" clip-path="url(#myCircle)"></image>
      </g>
    </svg>`;
  };

  const renderPie = function(dataGraph) {
    return `
    <div class="flex-column mb-3 font-smaller-2">
      <b class="mb-2">${dataGraph.strings.type}</b>
      <div class="d-flex align-items-center">
        <svg width="100%" height="100%" viewBox="0 0 42 42" class="user-card_pie-chart" style="border-radius: 50px;">
          <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#d2d3d4" stroke-width="31.830988618"></circle>
          <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke-dasharray="${dataGraph.percentsent} ${100 - dataGraph.percentsent}" stroke="${dataGraph.color}" stroke-width="31.830988618" stroke-dashoffset="25"></circle>
          <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke-dasharray="${dataGraph.percentreceived} ${100 - dataGraph.percentreceived}" stroke="${dataGraph.colorlight}" stroke-width="31.830988618" stroke-dashoffset="${(100 - dataGraph.percentsent) + 25 }"></circle>
        </svg>
        <div class="d-flex mx-2">
          <div class="ml-2">
            <b class="d-block">${dataGraph.amountsent}</b>
            <span class="text-black-60">${dataGraph.strings.sent}</span>
          </div>
          <div class="ml-2">
            <b class="d-block">${dataGraph.amountreceived}</b>
            <span class="text-black-60">${dataGraph.strings.received}</span>
          </div>
        </div>
      </div>
    </div>
    `;
  };

  const followBtn = function(data) {
    if (data.is_following) {
      return `<button class="btn btn-primary btn-sm px-2 font-caption" data-follow="${data.profile.handle}">Unfollow <i class="fas fa-user-minus font-smaller-4"></i></button>`;
    }
    return `<button class="btn btn-primary btn-sm px-2 font-caption" data-follow="${data.profile.handle}">Follow <i class="fas fa-user-plus font-smaller-4"></i></button>`;
  };

  return `
    <div class="popover-bounty__content">
      <div class="d-flex justify-content-between mb-2">
        <div class="d-flex align-items-end">
          ${renderAvatarData()}
          <div class="">
            ${orgs.length ? orgs : ''}
          </div>
        </div>
        <div>
          ${data.is_authenticated && data.profile.handle !== document.contxt.github_handle ? followBtn(data) : ''}
        </div>
      </div>
      <p class="d-block font-body my-auto">${data.profile.data.name || data.profile.handle}</p>
      <a href="/${data.profile.handle}" class="font-body font-weight-semibold">@${data.profile.handle}</a>

      <div class="my-2">

        <a class="btn btn-outline-primary btn-sm font-smaller-5" href="/tip?username=${data.profile.handle}" data-toggle="tooltip" data-container=".popover-user-card" data-original-title="Tip @${data.profile.handle}">
          <i class="fab fa-fw fa-ethereum"></i>
        </a>

        <a class="btn btn-outline-primary btn-sm font-smaller-5" href="/kudos/send?username=${data.profile.handle}" data-toggle="tooltip" data-container=".popover-user-card" data-original-title="Kudos @${data.profile.handle}">
          <i class="fas fa-fw fa-dice-d6"></i>
        </a>

        <a class="btn btn-outline-primary btn-sm font-smaller-5" href="/users?invite=${data.profile.handle}" data-toggle="tooltip" data-container=".popover-user-card" data-original-title="Invite @${data.profile.handle} to Bounty">
          <i class="fas fa-fw fa-envelope-open-text"></i>
        </a>
        |
        <a class="btn btn-outline-primary btn-sm font-smaller-5" href="https://github.com/${data.profile.handle}?tab=repositories" target="_blank" rel="noopener noreferrer" data-toggle="tooltip" data-container=".popover-user-card" data-original-title="@${data.profile.handle} on Github">
          <i class="fab fa-fw fa-github"></i>
        </a>
      </div>

      <div class="font-smaller-1 my-2">${data.profile.keywords.map(
    (keyword, index) => {
      if (index < 5) {
        return `<span class="badge badge--bluelight p-1">${keyword}</span>`;
      } else if (index < 6) {
        return `<span class="badge badge--bluelight p-1">+${data.profile.keywords.length - 5}</span>`;
      }
    }).join(' ')}</div>
      <div class="d-flex justify-content-between mb-2">
        <span class="text-black-60">
          Joined <time class="" datetime="${data.profile.created_on}" title="${data.profile.created_on}">${moment.utc(data.profile.created_on).fromNow()}</time>
        </span>
        ${data.profile_dict.scoreboard_position_funder ? `<span>#${data.profile_dict.scoreboard_position_funder} <span class="text-black-60">Funder</span></span>` : '' }
        ${data.profile_dict.scoreboard_position_contributor ? `<span>#${data.profile_dict.scoreboard_position_contributor} <span class="text-black-60">Contributor</span></span>` : '' }
      </div>

      <div class="d-flex flex-wrap justify-content-between">
      ${mount_graph.map((graph)=> renderPie(graph)).join(' ')}
      </div>

      <div class="d-flex">
        <span class="mr-3"><b class="font-smaller-1">${data.profile.followers}</b> <span class="text-black-60">Followers</span></span>
        <span><b class="font-smaller-1">${data.profile.following}</b> <span class="text-black-60">Following</span></span>
      </div>
    </div>
  `;
};

const cb = (handle, elem, response) => {
  $(elem).attr('disabled', false);
  popoverData.filter(item => item[handle])[0][handle].is_following = response.is_member;
  response.is_member ? $(elem).html('Unfollow <i class="fas fa-user-minus font-smaller-4"></i>') : $(elem).html('Follow <i class="fas fa-user-plus font-smaller-4"></i>');
};

const addFollowAction = () => {
  $('[data-follow]').each(function(index, elem) {
    $(elem).on('click', function(e) {
      $(elem).attr('disabled', true);

      const handle = $(elem).data('follow');
      const error = () => {
        $(elem).attr('disabled', false);
      };

      followRequest(handle, elem, cb, error);
    });

  });
};

function openContributorPopOver(contributor, element) {
  if (!contributor) {
    return;
  }

  const contributorURL = `/api/v0.1/user_card/${contributor}`;

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
        if (element.is(':hover')) {
          setupPopover(element, response);
        }
      })
      .catch(err => {
        return console.warn({ message: err });
      });
  } else {
    setupPopover(element, popoverData.filter(item => item[contributor])[0][contributor]);
  }
}

function setupPopover(element, data) {
  element.popover({
    sanitizeFn: function(content) {
      return DOMPurify.sanitize(content);
    },
    placement: 'auto',
    trigger: 'manual',
    template: `
      <div class="popover popover-user-card" role="tooltip">
        <div class="arrow"></div>
        <h3 class="popover-header"></h3>
        <div class="popover-body"></div>
      </div>`,
    content: function() {
      return renderPopOverData(data);
    },
    html: true
  });

  $(element).popover('show');

  addFollowAction();
}
