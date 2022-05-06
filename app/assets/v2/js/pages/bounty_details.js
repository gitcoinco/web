/* eslint block-scoped-var: "warn" */
/* eslint no-redeclare: "warn" */
/* eslint no-loop-func: "warn" */

const _truthy = function(val) {
  if (!val || val == '0x0000000000000000000000000000000000000000') {
    return false;
  }
  return true;
};

var address_ize = function(key, val) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="https://etherscan.io/address/' + val + '" target="_blank" rel="noopener noreferrer">' + val + '</a>' ];
};

var gitcoin_ize = function(key, val) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="/profile/' + val + '" target="_blank" rel="noopener noreferrer">' + val.replace('@', '') + '</a>' ];
};

var email_ize = function(key, val) {

  if (!validateEmail(val)) {
    $('#bounty_owner_email').remove();
    $('#bounty_owner_email_label').remove();
  }

  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="mailto:' + val + '">' + val + '</a>' ];
};

var hide_if_empty = function(key, val) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, val ];
};

var unknown_if_empty = function(key, val) {
  if (!_truthy(val)) {
    $('#' + key).parent().hide();
    return [ key, 'Unknown' ];
  }
  return [ key, val ];
};

var link_ize = function(key, val) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="' + val + '" target="_blank" rel="noopener noreferrer">' + val + '</a>' ];
};

const token_value_to_display = function(val) {
  if (!val) {
    return '';
  }
  return Math.round((parseInt(val) / Math.pow(10, document.decimals)) * 1000) / 1000;
};

// rows in the 'about' page
var rows = [
  'avatar_url',
  'issuer_avatar_url',
  'title',
  'event_name',
  'github_url',
  'value_in_token',
  'value_in_eth',
  'value_in_usdt',
  'token_value_in_usdt',
  'token_value_time_peg',
  'web3_created',
  'status',
  'project_type',
  'project_length',
  'permission_type',
  'bounty_owner_address',
  'bounty_owner_email',
  'issue_description',
  'bounty_owner_github_username',
  'fulfillments',
  'network',
  'experience_level',
  'reserved_for_user_handle',
  'bounty_type',
  'expires_date',
  'issue_keywords',
  'bounty_categories',
  'started_owners_username',
  'submitted_owners_username',
  'fulfilled_owners_username',
  'fulfillment_accepted_on',
  'additional_funding_summary',
  'admin_override_suspend_auto_approval'
];

var heads = {
  'avatar_url': gettext('Issue'),
  'value_in_token': gettext('Issue Funding Info'),
  'bounty_owner_address': gettext('Funder'),
  'fulfiller_address': gettext('Submitter'),
  'experience_level': gettext('Meta')
};

var callbacks = {
  'github_url': link_ize,
  'value_in_token': function(key, val, result) {
    const title = token_value_to_display(val) + ' ' + result['token_name'];
    const title_expand = title + ' in funding from original funder.';

    $('#value_in_token').parents('.token').attr('title', title_expand);
    return [ 'amount', title ];
  },
  'avatar_url': function(key, val, result) {
    return [ 'avatar', '<a href="/profile/' + result['org_name'] + '"><img class="avatar ' + result['github_org_name'] + '" src="' + val + '"></a>' ];
  },
  'issuer_avatar_url': function(key, val, result) {
    const username = result['bounty_owner_github_username'] ? result['bounty_owner_github_username'] : 'Self';

    return [ 'issuer_avatar_url', '<a href="/profile/' + result['bounty_owner_github_username'] +
      '"><img class=avatar src="/dynamic/avatar/' + username + '"></a>' ];
  },
  'status': function(key, val, result) {
    let ui_status = val;
    let ui_status_raw = val;

    if (ui_status_raw === 'open') {
      ui_status = '<span>' + gettext('OPEN ISSUE') + '</span>';

      let can_submit = result['can_submit_after_expiration_date'];

      if (!isBountyOwner(result) && can_submit && is_bounty_expired(result)) {
        ui_status += '<p class="text-highlight-light-blue font-weight-light font-body" style="text-transform: none;">' +
          gettext('This issue is past its expiration date, but it is still active.') +
          '<br>' +
          gettext('Check with the submitter to see if they still want to see it fulfilled.') +
          '</p>';
      }
    } else if (ui_status_raw === 'started') {
      ui_status = '<span>' + gettext('work started') + '</span>';
    } else if (ui_status_raw === 'submitted') {
      ui_status = '<span>' + gettext('work submitted') + '</span>';
    } else if (ui_status_raw === 'done') {
      ui_status = '<span>' + gettext('done') + '</span>';
    } else if (ui_status_raw === 'cancelled') {
      ui_status = '<span style="color: #f9006c;">' + gettext('cancelled') + '</span>';
    }

    if (isBountyOwner(result) && is_bounty_expired(result) &&
      ui_status_raw !== 'done' && ui_status_raw !== 'cancelled') {

      ui_status += '<p class="font-weight-light font-body" style="color: black; text-transform: none;">' +
      'This issue has expired. Click <a class="text-highlight-light-blue font-weight-semibold" href="/extend-deadlines">here to extend expiration</a> ' +
      'before taking any bounty actions. </p>';
    }

    return [ 'status', ui_status ];
  },
  'event_name': function(key, val, result) {
    let event_name = result['event'] ? 'Hackathon: ' + result.event.name : '';

    return [ 'event_name', event_name ];
  },
  'issue_description': function(key, val, result) {

    const _markdown = new markdownit({
      linkify: true,
      highlight: function(str, lang) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return '<pre class="hljs"><code>' +
                    hljs.highlight(lang, str, true).value +
                   '</code></pre>';
          } catch (__) {}
        }
        return '<pre class="hljs"><code>' + sanitize(_markdown.utils.escapeHtml(str)) + '</code></pre>';
      }
    });

    _markdown.renderer.rules.table_open = function() {
      return '<table class="table">';
    };
    ui_body = sanitize(_markdown.render(val));
    return [ 'issue_description', ui_body ];
  },
  'bounty_owner_address': address_ize,
  'bounty_owner_email': email_ize,
  'experience_level': unknown_if_empty,
  'project_length': unknown_if_empty,
  'bounty_type': unknown_if_empty,
  'bounty_owner_github_username': gitcoin_ize,
  'funding_organisation': function(key, val, result) {
    return [ 'funding_organisation', result.funding_organisation ];
  },
  'bounty_categories': function(key, val, result) {
    if (!result.bounty_categories || result.bounty_categories.length == 0)
      return [ 'bounty_categories', null ];

    const categories = [];
    const categoryObj = {
      frontend: '<span class="badge badge-secondary mr-1"><i class="fas fa-laptop-code"></i> Front End</span>',
      backend: '<span class="badge badge-secondary mr-1"><i class="fas fa-code"></i> Back End</span>',
      design: '<span class="badge badge-secondary mr-1"><i class="fas fa-pencil-ruler"></i> Design</span>',
      documentation: '<span class="badge badge-secondary mr-1"><i class="fas fa-file-alt"></i> Documentation</span>',
      other: '<span class="badge badge-secondary mr-1"><i class="fas fa-briefcase"></i> Other</span>'
    };

    result.bounty_categories.forEach(function(category) {
      categories.push(categoryObj[category]);
    });
    return [ 'bounty_categories', categories ];
  },
  'permission_type': function(key, val, result) {
    if (val == 'approval') {
      val = 'Approval Required';
    }
    return [ 'permission_type', ucwords(val) ];
  },
  'project_type': function(key, val, result) {
    return [ 'project_type', ucwords(result.project_type) ];
  },
  'admin_override_suspend_auto_approval': function(key, val, result) {
    if (result['permission_type'] === 'approval') {
      $('#auto_approve_workers_wrapper').show();
    } else {
      $('#auto_approve_workers_wrapper').hide();
    }
    return [ 'admin_override_suspend_auto_approval', val ? 'Off' : 'On' ];
  },
  'issue_keywords': function(key, val, result) {
    if (!result.keywords || result.keywords.length == 0)
      return [ 'issue_keywords', null ];


    var keywords = result.keywords && result.keywords.split ? result.keywords.split(',') : result.keywords;
    var tags = [];

    keywords.forEach(function(keyword) {
      keyword = keyword.replace(/[\W_]+/g, '');
      tags.push('<a href="/explorer/?q=' + keyword.trim() + '"><div class="tag keyword">' + keyword + '</div></a>');
    });
    return [ 'issue_keywords', tags ];
  },
  'value_in_eth': function(key, val, result) {
    if (result['token_name'] == 'ETH' || val === null) {
      return [ null, null ];
    }
    return [ 'Amount (ETH)', Math.round((parseInt(val) / Math.pow(10, 18)) * 1000) / 1000 ];
  },
  'value_in_usdt': function(key, val, result) {
    if (val === null) {
      return [ null, null ];
    }

    $('#value_in_usdt_wrapper').attr('title', '<div class="tooltip-info">The funding in this bounty adds up to $' + val + ' USD </div>');

    return [ 'Amount_usd', val ];
  },
  'fulfillment_accepted_on': function(key, val, result) {
    if (val === null || typeof val == 'undefined') {
      $('#fulfillment_accepted_on_wrapper').addClass('hidden');
      return [ null, null ];
    }
    var timePeg = timeDifference(new Date(), new Date(val), false, 60 * 60);

    return [ 'fulfillment_accepted_on', timePeg ];
  },
  'network': function(key, val, result) {
    if (val.toLowerCase().indexOf('mainnet') >= 0) {
      $('#network').addClass('hidden');
      return [ null, null ];
    }
    var warning = 'WARNING: this is a ' + val + ' network bounty, and is NOT real money.  To see mainnet bounties, go to <a href="/explorer">the bounty explorer</a> and search for mainnet bounties.  ';

    return [ 'network', warning ];
  },
  'additional_funding_summary': function(key, val, result) {

    const tokens = Object.keys(val);

    if (tokens.length === 0) {
      return [ key, val ];
    }

    const tokenDecimals = 3;
    const bountyTokenName = result['token_name'];
    const bountyTokenAmount = token_value_to_display(result['value_in_token'], tokenDecimals);
    const dateNow = new Date();
    const dateTokenValue = new Date(result['token_value_time_peg']);
    const timePeg = timeDifference(dateNow, dateTokenValue > dateNow ? dateNow : dateTokenValue, false, 60 * 60);
    const usdTagElement = document.querySelector('#value_in_usdt_wrapper');
    const container = document.querySelector('.tags');

    let leftHtml = '';
    let rightHtml = '';

    leftHtml += '<p class="m-0">&nbsp;&nbsp;&nbsp;' +
      bountyTokenAmount + ' ' + bountyTokenName + '</p>';

    rightHtml += '<p class="m-0">@ $' +
      result['token_value_in_usdt'] + ' ' + bountyTokenName + ' as of ' + timePeg + '</p>';

    let totalUSDValue = parseFloat(result['value_in_usdt']) || 0.0;

    while (tokens.length) {
      const tokenName = tokens.shift();
      const obj = val[tokenName];
      const ratio = obj['ratio'];
      const amount = obj['amount'];
      const usd = amount * ratio;
      const funding = round(amount, 2);
      const tokenValue = Math.round(1.0 * ratio);
      const timestamp = new Date(obj['timestamp']);
      const timePeg = timeDifference(dateNow, timestamp > dateNow ? dateNow : timestamp, false, 60 * 60);
      const tooltip = `+ ${funding} ${tokenName} in crowdfunding`;

      leftHtml += '<p class="m-0">+ ' + funding + ' ' + tokenName + '</p>';
      rightHtml += '<p class="m-0">@ $' + tokenValue + ' ' + tokenName + ' as of ' + timePeg + '</p>';

      totalUSDValue += usd;

      container.insertBefore(
        newTokenTag(funding, tokenName, tooltip, true),
        usdTagElement
      );

    }

    $('#value_in_usdt').html(Math.round(totalUSDValue));

    $('#value_in_usdt_wrapper').attr('title',
      '<div class="tooltip-info tooltip-sm">' +
      '<p class="text-highlight-gc-purple">How did we calculate this?</p>' +
      '<div style="float:left; text-align:left;">' +
      leftHtml +
      '</div><div style="margin-left: .5rem; float:right; text-align:left;">' +
      rightHtml +
      '</div></div>'
    );

    return [ key, val ];
  },
  'token_value_time_peg': function(key, val, result) {
    if (val === null || typeof val == 'undefined') {
      $('#token_value_time_peg_wrapper').addClass('hidden');
      return [ null, null ];
    }
    var timePeg = timeDifference(new Date(), new Date(val), false, 60 * 60);

    return [ 'token_value_time_peg', timePeg ];
  },
  'token_value_in_usdt': function(key, val, result) {
    if (val === null || typeof val == 'undefined') {
      $('#value_in_usdt_wrapper').addClass('hidden');
      return [ null, null ];
    }
    return [ 'Token_amount_usd', '$' + val + '/' + result['token_name'] ];
  },
  'web3_created': function(key, val, result) {
    return [ 'updated', timeDifference(new Date(result['now']), new Date(result['web3_created'])) ];
  },
  'expires_date': function(key, val, result) {
    moment.locale('en-expire');
    moment.defineLocale('en-expire', {
      parentLocale: 'en',
      relativeTime: {
        future: '%s'
      }
    });
    expires_date = new Date(val);
    let label = 'expires';
    let response = moment.utc(expires_date).fromNow();
    const isInfinite = expires_date - new Date().setFullYear(new Date().getFullYear() + 1) > 1;

    $('#expires_date').attr('title', moment(expires_date).format('LLL'));

    if (expires_date < new Date()) {
      label = 'expired';
      if (result['is_open']) {
        $('.timeleft').text('Expired');
      }
    } else if (isInfinite) {
      $('#expires_date').removeAttr('title');
      response = 'Never expires';
    }

    return [ label, response ];
  },
  'started_owners_username': function(key, val, result) {
    let started = [];
    let uniqueness = [];

    if (result.interested) {
      let interested = result.interested;

      interested.forEach(function(_interested, position) {
        const name = (position == interested.length - 1) ?
          _interested.profile.handle : _interested.profile.handle.concat(',');

        if (
          !_interested.pending &&
          uniqueness.indexOf(_interested.profile.handle) == -1
        ) {
          uniqueness.push(_interested.profile.handle);
          started.push(profileHtml(_interested.profile.handle, name));
        }
      });
      if (started.length == 0)
        started.push('<i class="fas fa-minus"></i>');
    }
    return [ 'started_owners_username', started ];
  },
  'submitted_owners_username': function(key, val, result) {
    let accepted = [];
    let uniqueness = [];

    if (result.fulfillments) {
      let submitted = result.fulfillments;

      submitted.forEach(function(_submitted, position) {
        const name = (position == submitted.length - 1) ?
          _submitted.fulfiller_github_username : _submitted.fulfiller_github_username.concat(',');

        if (uniqueness.indexOf(_submitted.profile.handle) == -1) {
          uniqueness.push(_submitted.profile.handle);
          accepted.push(profileHtml(_submitted.fulfiller_github_username, name));
        }
      });
      if (accepted.length == 0) {
        accepted.push('<i class="fas fa-minus"></i>');
      }
    }
    return [ 'submitted_owners_username', accepted ];
  },
  'fulfilled_owners_username': function(key, val, result) {
    let accepted = [];

    if (result.paid) {
      if (result.paid.length == 0) {
        accepted.push('<i class="fas fa-minus"></i>');
      } else {
        result.paid.forEach((github_username, position) => {
          const name = (position == result.paid.length - 1) ?
            github_username : github_username.concat(',');

          accepted.push(profileHtml(github_username, name));
        });
      }
    }
    return [ 'fulfilled_owners_username', accepted ];
  },
  'reserved_for_user_handle': function(key, val, bounty) {
    if (val) {
      if (bounty['is_reserved'] && bounty['status'] === 'reserved') {
        const reservedForHtmlLink = '<a href="/profile/' + val + '">' + val + '</a>';
        const reservedForAvatar = '<img class="rounded-circle" src="/dynamic/avatar/' + val + '" width="25" height="25"/>';

        $('#bounty_reserved_for').html(reservedForHtmlLink + reservedForAvatar);
        return [ key, val ];
      }
    }

    $('#bounty_reserved_for').css('display', 'none');
    $('#bounty_reserved_for_label').css('display', 'none');

    return [ key, val ];
  }
};

const isAvailableIfReserved = function(bounty) {
  const reservedFor = bounty['reserved_for_user_handle'];

  if (reservedFor) {
    if (caseInsensitiveCompare(reservedFor, document.contxt['github_handle'])) {
      return true;
    }

    if (bounty['is_reserved']) {
      return false;
    }
  }

  return true;
};

const isBountyOwner = result => {
  if (is_bounties_network) {
    return isFundedByCurrentAddress(result) && isBountyOwnerPerLogin(result);
  }
  return isBountyOwnerPerLogin(result);
};

const isFundedByCurrentAddress = result => {
  if (
    typeof web3 == 'undefined' || !web3.eth ||
    typeof cb_address == 'undefined' || !cb_address || !result
  ) {
    return false;
  }
  return caseInsensitiveCompare(cb_address, result['bounty_owner_address']);
};

const isBountyOwnerPerLogin = result => {
  return caseInsensitiveCompare(
    result['bounty_owner_github_username'], document.contxt['github_handle']
  );
};

var update_title = function() {
  document.original_title_text = $('title').text();
  setInterval(function() {
    if (document.prepend_title == '(...)') {
      document.prepend_title = '(*..)';
    } else if (document.prepend_title == '(*..)') {
      document.prepend_title = '(.*.)';
    } else if (document.prepend_title == '(.*.)') {
      document.prepend_title = '(..*)';
    } else {
      document.prepend_title = '(...)';
    }
    $('title').text(document.prepend_title + ' ' + document.original_title_text);
  }, 2000);
};

var showWarningMessage = function(txid) {
  console.log(txid);
  const secondsBetweenQuoteChanges = 30;
  let interval = setInterval(waitingRoomEntertainment, secondsBetweenQuoteChanges * 1000);

  update_title();
  $('.interior .body').addClass('open');
  $('.interior .body').addClass('loading');

  if (typeof txid != 'undefined' && txid.indexOf('0x') != -1) {
    waitforWeb3(function() {
      clearInterval(interval);
      var link_url = get_etherscan_url(txid);

      $('#transaction_url').attr('href', link_url);
    });
  }

  $('.left-rails').hide();
  $('#bounty_details').hide();

  waitingStateActive();
  show_invite_users();
};

// refresh page if metamask changes
// waitforWeb3(function() {
//   setInterval(function() {
//     if (document.web3Changed) {
//       return;
//     }
//     reloadCbAddress();

//     if (typeof document.lastWeb3Network == 'undefined') {
//       document.lastWeb3Network = document.web3network;
//       return;
//     }

//     if (typeof document.lastCoinbase == 'undefined') {

//       web3.eth.getCoinbase(function(error, coinbase) {
//         if (error) {
//           console.log('web3.eth.coinbase could not be loaded');
//           document.lastCoinbase = null;
//           return;
//         }
//         document.lastCoinbase = coinbase;
//       });
//       return;
//     }

//     if (web3 && (document.lastCoinbase != cb_address) ||
//       (document.lastWeb3Network != document.web3network)) {
//       _alert(gettext('Detected a web3 change.  Refreshing the page. '), 'info');
//       document.location.reload();
//       document.web3Changed = true;
//     }

//   }, 500);
// });

var wait_for_tx_to_mine_and_then_ping_server = function() {
  console.log('checking for updates');
  if (typeof document.pendingIssueMetadata != 'undefined') {
    var txid = document.pendingIssueMetadata.txid.transactionHash;

    console.log('waiting for web3 to be available');
    callFunctionWhenweb3Available(function() {
      console.log('waiting for tx to be mined');
      callFunctionWhenTransactionMined(txid, function() {
        console.log('tx mined');
        var data = {
          url: document.issueURL,
          txid: txid,
          network: document.web3network
        };
        var error = function(response) {
          // refresh upon error
          document.location.reload();
        };
        var success = function(response) {
          if (response.status == '200') {
            console.log('success from sync/web', response);

            // clear local data
            delete sessionStorage['fulfillers'];
            delete sessionStorage['bountyId'];
            localStorage[document.issueURL] = '';
            if (response['url']) {
              document.location.href = response['url'];
            } else {
              document.location.reload();
            }
          } else {
            console.log('error from sync/web', response);
            error(response);
          }
        };

        console.log('syncing gitcoin with web3');
        var uri = '/sync/web3/';

        $.ajax({
          type: 'POST',
          url: uri,
          data: data,
          success: success,
          error: error,
          dataType: 'json'
        });
      });
    });
  }
};

var attach_work_actions = function() {
  $('body').delegate('a[href="/interested"], a[href="/uninterested"], a[href="/extend-deadlines"]', 'click', function(e) {
    e.preventDefault();
    if ($(this).attr('href') == '/interested') {
      show_interest_modal.call(this);
    } else if ($(this).attr('href') === '/extend-deadlines') {
      show_extend_deadline_modal.call(this);
    } else if (confirm(gettext('Are you sure you want to stop work?'))) {
      $(this).attr('href', '/interested');
      $(this).find('span').text(gettext('Start Work'));
      $(this).parent().attr('title', '<div class="tooltip-info tooltip-sm">' + gettext('Notify the funder that you would like to take on this project') + '</div>');
      remove_interest(document.result['pk']);
    }
  });
};

var attach_contact_funder_options = function() {
  $('body').delegate('a.contact_bounty_hunter', 'click', function(e) {
    e.preventDefault();
    var text = window.prompt('What would you like to say to the funder?', '');
    var connector_char = document.location.href.indexOf('?') == -1 ? '?' : '&';
    var url = document.location + connector_char + 'admin_contact_funder=' + text;

    document.location.href = url;
  });
};


var attach_snoozee_options = function() {
  $('body').delegate('a.snooze_gitcoin_bot', 'click', function(e) {
    e.preventDefault();
    var text = window.prompt('How many days do you want to snooze?', '');
    var connector_char = document.location.href.indexOf('?') == -1 ? '?' : '&';
    var url = document.location + connector_char + 'snooze=' + text;

    document.location.href = url;
  });
};

var attach_override_status = function() {
  $('body').delegate('a.admin_override_satatus', 'click', function(e) {
    e.preventDefault();
    var text = window.prompt('What new status (valid choices: "open", "started", "submitted", "done", "expired", "cancelled", "" to remove override )?', '');
    var connector_char = document.location.href.indexOf('?') == -1 ? '?' : '&';
    var url = document.location + connector_char + 'admin_override_satatus=' + text;

    document.location.href = url;
  });
};

const submitInterest = (bounty, msg, self, onSuccess) => {
  add_interest(bounty, {
    issue_message: msg
  }).then(success => {
    if (success) {
      $(self).attr('href', '/uninterested');
      $(self).find('span').text(gettext('Stop Work'));
      $(self).parent().attr('title', '<div class="tooltip-info tooltip-sm">' + gettext('Notify the funder that you will not be working on this project') + '</div>');


      if (onSuccess) {
        onSuccess();
      }
    }
  }).catch((error) => {
    if (error.responseJSON.error === 'You may only work on max of 3 issues at once.')
      return;
    throw error;
  });
};

const show_interest_modal = () => {
  let self = this;
  let modals = $('#modalInterest');
  let modalBody = $('#modalInterest .modal-content');
  let modalUrl = `/interest/modal?redirect=${window.location.pathname}&pk=${document.result['pk']}`;

  modals.on('show.bs.modal', function() {
    modalBody.load(modalUrl, ()=> {
      let actionPlanForm = $('#action_plan');
      let issueMessage = $('#issue_message');
      let data = $('.team-users').data('initial') ? $('.team-users').data('initial').split(', ') : [];
      let projectForm = $('#projectForm');

      $('#looking-members').on('click', function() {
        $('.looking-members').toggle();
      });
      userSearch('.team-users', false, '', data, true, false);
      issueMessage.attr('placeholder', gettext('What steps will you take to complete this task? (min 30 chars)'));

      if (document.result.event) {
        $(document).on('change', '#project_logo', function() {
          previewFile($(this));
        });
        projectForm.on('submit', function(e) {
          e.preventDefault();
          let elements = $(this)[0];
          let logo = elements['logo'].files[0];
          let data = $(this).serializeArray();
          let summary = elements['summary'].value;

          submitInterest(document.result['pk'], summary, self, () => {
            submitProject(logo, data);
            modals.bootstrapModal('hide');
          });
        });

        return;
      }

      actionPlanForm.on('submit', function(event) {
        event.preventDefault();

        let msg = issueMessage.val().trim();

        if (!msg || msg.length < 30) {
          _alert({message: gettext('Please provide an action plan for this ticket. (min 30 chars)')}, 'danger');
          return false;
        }

        submitInterest(document.result['pk'], msg, self, () => {
          modals.bootstrapModal('hide');
        });
      });

    });
  });
  modals.bootstrapModal('show');
};


var set_extended_time_html = function(extendedDuration) {
  extendedDuration = extendedDuration.set({hour: 0, minute: 0, second: 0, millisecond: 0});
  $('input[name=updatedExpires]').val(extendedDuration.utc().unix());
  $('#extended-expiration-date #extended-date').html(extendedDuration.format('MM-DD-YYYY hh:mm A'));
  $('#extended-expiration-date #extended-days').html(moment.utc(extendedDuration).fromNow());
};

var show_extend_deadline_modal = function() {
  let modals = $('#modalExtend');
  let modalBody = $('#modalExtend .modal-content');
  const url = '/modal/extend_issue_deadline?pk=' + document.result['pk'];

  moment.locale('en');
  modals.on('show.bs.modal', function() {
    modalBody.load(url, ()=> {
      const currentExpires = moment.utc(document.result['expires_date']);

      $('#modalExtend input[name="expirationTimeDelta"]').daterangepicker({
        parentEl: '#extend_deadline',
        singleDatePicker: true,
        startDate: moment(currentExpires).add(1, 'month'),
        minDate: moment().add(1, 'day'),
        ranges: {
          '1 week': [ moment(currentExpires).add(7, 'days'), moment(currentExpires).add(7, 'days') ],
          '2 weeks': [ moment(currentExpires).add(14, 'days'), moment(currentExpires).add(14, 'days') ],
          '1 month': [ moment(currentExpires).add(1, 'month'), moment(currentExpires).add(1, 'month') ],
          '3 months': [ moment(currentExpires).add(3, 'month'), moment(currentExpires).add(3, 'month') ],
          '1 year': [ moment(currentExpires).add(1, 'year'), moment(currentExpires).add(1, 'year') ]
        },
        'locale': {
          'customRangeLabel': 'Custom'
        }
      }, function(start, end, label) {
        set_extended_time_html(end);
      });

      set_extended_time_html($('#modalExtend input[name="expirationTimeDelta"]').data('daterangepicker').endDate);

      $('#neverExpires').on('click', () => {
        if ($('#neverExpires').is(':checked')) {
          $('#expirationTimeDelta').attr('disabled', true);
          $('#extended-expiration-date #extended-days').html('Never');
          $('#extended-expiration-date #extended-date').html('-');
        } else {
          $('#expirationTimeDelta').attr('disabled', false);
          set_extended_time_html($('#modalExtend input[name="expirationTimeDelta"]').data('daterangepicker').endDate);
        }
      });

      modals.on('submit', function(event) {
        event.preventDefault();

        var extended_time = $('input[name=updatedExpires]').val();

        extend_expiration(document.result['pk'], {
          deadline: extended_time
        });
        setTimeout(function() {
          window.location.reload();
        }, 2000);
      });
    });
  });
  modals.bootstrapModal('show');
  $(document, modals).on('hidden.bs.modal', function(e) {
    $('#extend_deadline').remove();
    $('.daterangepicker').remove();
  });
};

const showGithubSync = function(result) {
  if (isBountyOwnerPerLogin(result) || currentProfile.isStaff) {
    $('#bounty-options-link').append(
      `<a id="sync-github-issue" class="dropdown-item p-2">
        <i class="fas fa-sync mr-2"></i>
        Sync Issue
      </a>`
    );

    $('#sync-github-issue').on('click', function(event) {
      event.preventDefault();
      const bountyId = result.pk;

      $.get(
        '/sync/get_issue_details?url=' + encodeURIComponent(result['github_url']) + '&token=' + currentProfile.githubToken
      ).then(function(result) {
        const payload = JSON.stringify({
          issue_description: result.description,
          title: result.title
        });

        return $.post('/bounty/change/' + bountyId, payload).then(
          function(result) {
            result = sanitizeAPIResults(result);
            _alert({ message: result.msg }, 'success');

            if (result.url) {
              setTimeout(function() {
                document.location.href = result.url;
              }, 1000);
            }
          }
        ).fail(
          function(result) {
            const alertMsg = result && result.responseJSON ? result.responseJSON.error : gettext('Failed to sync issue. Please reload the page and try again.');

            _alert({ message: alertMsg }, 'danger');
          }
        );
      }).fail(function(result) {
        const alertMsg = result && result.responseJSON ? result.responseJSON.error : gettext('Failed to sync issue. Please reload the page and try again.');

        _alert({ message: alertMsg }, 'danger');
      });
    });
  }
};

var build_detail_page = function(result) {

  // setup
  var decimals = 18;
  var related_token_details = tokenAddressToDetailsByNetwork(result['token_address'], result['network']);

  if (related_token_details && related_token_details.decimals) {
    decimals = related_token_details.decimals;
  }
  document.decimals = decimals;
  $('#bounty_details').css('display', 'inline');

  // title
  result['title'] = result['title'] ? result['title'] : result['github_url'];
  $('.title').html(gettext('Funded Issue Details: ') + result['title']);

  // funded by
  if (
    isBountyOwnerPerLogin(result) &&
    !isFundedByCurrentAddress(result)
  ) {
    $('#funder_notif_info').html(
      gettext('Funder Address: ') +
      '<span id="bounty_funded_by">' +
      result['bounty_owner_address'] + '</span>'
    );
    $('#funder_notif_info').append('\
      <span class="bounty-notification ml-2">\
        <i class="far fa-bell mr-2"></i>\
        Ready to Pay? Set Your Metamask to this address!\
        <img src="' + static_url + 'v2/images/metamask.svg" class="ml-2">\
      </span>'
    );
  }

  // insert table onto page
  for (var j = 0; j < rows.length; j++) {
    var key = rows[j];
    var head = null;
    var val = result[key];

    if (heads[key]) {
      head = heads[key];
    }
    if (callbacks[key]) {
      _result = callbacks[key](key, val, result);
      val = _result[1];
    }

    hljs.initHighlighting.called = false;
    hljs.initHighlighting();

    var id = '#' + key;

    if ($(id).length) {
      $(id).html(val);
    }
  }

  $('body').delegate('#bounty_details .button.disabled', 'click', function(e) {
    e.preventDefault();
  });

  $('#bounty_details #issue_description img').on('click', function() {

    var content = $.parseHTML(
      '<div><div class="row"><div class="col-12 closebtn">' +
        '<a id="" rel="modal:close" href="javascript:void" class="close" aria-label="Close dialog">' +
          '<span aria-hidden="true">&times;</span>' +
        '</a>' +
      '</div>' +
      '<div class="col-12 pt-2 pb-2"><img class="magnify" src="' + $(this).attr('src') + '"/></div></div></div>');

    $(content).appendTo('body').modal({
      modalClass: 'modal magnify'
    });
  });

  showGithubSync(result);
};

const is_current_user_interested = function(result) {
  if (!document.contxt.github_handle) {
    return false;
  }
  return !!(result.interested || []).find(interest => caseInsensitiveCompare(interest.profile.handle, document.contxt.github_handle));
};

const is_current_user_approved = function(result) {
  if (!document.contxt.github_handle) {
    return false;
  }
  const needs_approval = result['permission_type'] === 'approval';
  const interested = result.interested || [];
  let len = interested.length;

  while (len--) {
    const interest = interested[len];
    const handle = interest.profile ? interest.profile.handle : '';

    if (handle && caseInsensitiveCompare(handle, document.contxt.github_handle)) {
      return needs_approval ? interest.pending === false : true;
    }
  }

  return false;
};

const is_funder_notifiable = (result) => {
  if (result['funder_last_messaged_on']) {
	      return false;
  }
  return true;
};

var do_actions = function(result) {
  const is_legacy = result['web3_type'] == 'legacy_gitcoin';
  const is_status_expired = result['status'] == 'expired';
  const is_status_done = result['status'] == 'done';
  const is_status_cancelled = result['status'] == 'cancelled';
  const can_submit_after_expiration_date = result['can_submit_after_expiration_date'];
  const is_still_on_happy_path = result['status'] == 'reserved' || result['status'] == 'open' || result['status'] == 'started' || result['status'] == 'submitted' || (can_submit_after_expiration_date && result['status'] == 'expired');
  const needs_review = result['needs_review'];
  const is_open = result['is_open'];

  let bounty_path = result['network'] + '/' + result['standard_bounties_id'];

  const is_interested = is_current_user_interested(result);

  const has_fulfilled = result['fulfillments'].filter(fulfiller =>
    caseInsensitiveCompare(fulfiller.fulfiller_github_username, document.contxt['github_handle'])
  ).length > 0;

  document.interested = is_interested;

  const current_user_is_approved = is_current_user_approved(result);

  const should_block_from_starting_work =
    !is_interested &&
    result['project_type'] == 'traditional' &&
    (result['status'] == 'started' || result['status'] == 'submitted');

  let show_start_stop_work =
    is_still_on_happy_path &&
    !should_block_from_starting_work &&
    is_open &&
    !isBountyOwner(result) &&
    isAvailableIfReserved(result) &&
    !has_fulfilled;

  let show_github_link = result['github_url'].substring(0, 4) == 'http';
  let show_submit_work = is_open && !has_fulfilled;
  let show_kill_bounty = !is_status_done && !is_status_expired && !is_status_cancelled && isBountyOwner(result);
  let show_job_description = result['attached_job_description'] && result['attached_job_description'].startsWith('http');
  const show_increase_bounty = !is_status_done && !is_status_expired && !is_status_cancelled && is_bounties_network && isBountyOwner(result);
  const submit_work_enabled = !isBountyOwner(result) && current_user_is_approved;
  const notify_funder_enabled = is_funder_notifiable(result);
  let show_payout = !is_status_expired && !is_status_done && isBountyOwner(result) && !is_status_cancelled;
  let show_extend_deadline = isBountyOwner(result) && !is_status_expired && !is_status_done;
  let show_invoice = isBountyOwner(result);
  let show_notify_funder = is_open && has_fulfilled;


  const show_suspend_auto_approval = currentProfile.isStaff && result['permission_type'] == 'approval' && !result['admin_override_suspend_auto_approval'];
  const show_admin_methods = currentProfile.isStaff;
  const show_moderator_methods = currentProfile.isModerator;
  const show_change_bounty = is_still_on_happy_path && (isBountyOwner(result) || show_admin_methods);

  if (is_legacy) {
    show_start_stop_work = false;
    show_github_link = true;
    show_submit_work = false;
    show_kill_bounty = false;
    show_accept_submission = false;
  }

  // actions
  let actions = [];

  if (show_submit_work) {
    const enabled = submit_work_enabled;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['fulfill'],
      text: gettext('Submit Work'),
      parent: 'bounty_actions',
      title: gettext('Submit work for the funder to review'),
      work_started: is_interested,
      primary: true,
      id: 'submit'
    };

    actions.push(_entry);
  }

  if (show_notify_funder) {
    const enabled = notify_funder_enabled;
    const url = '/' + bounty_path + '/modal/funder_payout_reminder/';
    const _entry = {
	    enabled: enabled,
	    href: '#',
	    text: gettext('Send Payment Reminder'),
	    parent: 'bounty_actions',
	    title: gettext('Send Payment Reminder'),
	    id: 'notifyFunder',
	    clickhandler: show_modal_handler(url),
	    modal: true
	  };

    actions.push(_entry);
  }

  if (show_start_stop_work) {
    const enabled = true;
    let text;

    if (result['permission_type'] === 'approval')
      text = is_interested ? gettext('Stop Work') : gettext('Express Interest');
    else
      text = is_interested ? gettext('Stop Work') : gettext('Start Work');

    const interest_entry = {
      enabled: enabled,
      href: is_interested ? '/uninterested' : '/interested',
      text: text,
      parent: 'bounty_actions',
      title: is_interested ? gettext('Notify the funder that you will not be working on this project') : gettext('Notify the funder that you would like to take on this project'),
      id: 'interest',
      primary: true
    };

    actions.push(interest_entry);
  }

  if (result['is_reserved'] && result['status'] === 'reserved' &&
      caseInsensitiveCompare(result['reserved_for_user_handle'], document.contxt['github_handle'])) {
    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';

    const release_to_public_entry = {
      enabled: true,
      href: result['url'] + connector_char + 'release_to_public=1',
      text: gettext('Release Bounty'),
      parent: 'bounty_actions',
      title: gettext('Release this reserved bounty to the public')
    };

    actions.push(release_to_public_entry);
  }

  if (show_payout) {
    const enabled = isBountyOwner(result);
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['payout'],
      text: '<i class=\'fab fa-ethereum mr-2\'></i> Payout Bounty',
      title: gettext('Payout the bounty to one or more submitters.'),
      primary: true,
      parent: 'bounty_actions'
    };

    actions.push(_entry);
  }


  if (show_increase_bounty) {
    const enabled = true;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['increase'],
      text: isBountyOwner(result) ? gettext('Increase Funding') : gettext('Contribute Funds'),
      parent: 'bounty_actions',
      title: gettext('Help by funding or promoting this issue')
    };

    actions.push(_entry);
  }

  if (show_invoice) {
    $('#bounty-options-link').append(
      `<a href="${result['action_urls']['invoice']}" class="dropdown-item p-2" target="_blank">
        <i class="fas fa-file-alt mr-2"></i>
        Show Invoice
      </a>`
    );
  }

  if (show_change_bounty) {
    $('#bounty-options-link').append(
      `<a href="/bounty/change/${result['pk']}" class="dropdown-item p-2">
        <i class="fas fa-edit mr-2"></i>
        Update Details
      </a>`
    );

    if (show_extend_deadline) {
      $('#bounty-options-link').append(
        `<a href="/extend-deadlines" class="dropdown-item p-2">
          <i class="far fa-calendar-plus mr-2"></i>
          Extend Deadline
        </a>`
      );
    }

    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';
    const remarket_url = result['url'] + connector_char + 'trigger_remarket=1';

    if (result['can_remarket']) {
      $('#bounty-options-link').append(
        `<a href="${remarket_url}" class="dropdown-item p-2">
          <i class="fas fa-bullhorn mr-2"></i>
          Remarket Issue
        </a>`
      );
    }
  }

  if (show_github_link) {
    let github_url = result['github_url'];
    // hack to get around the renamed repo for piper's work.  can't change the data layer since blockchain is immutable

    github_url = github_url.replace('pipermerriam/web3.py', 'ethereum/web3.py');
    github_url = github_url.replace('ethereum/browser-solidity', 'ethereum/remix-ide');

    const _entry = {
      enabled: true,
      href: github_url,
      text: '<i class="fab fa-github mr-2"></i>' + gettext('View On Github'),
      parent: 'github_actions',
      title: gettext('View issue details and comments on Github')
    };

    actions.push(_entry);
  }

  if (show_kill_bounty) {
    $('#bounty-options-link').append(
      `<a href="${result['action_urls']['cancel']}" class="dropdown-item p-2">
        <i class="fas fa-times mr-2"></i>
        Cancel Bounty
      </a>`
    );
  }

  if (show_job_description) {
    $('#bounty-options-link').append(
      `<a href="${result['attached_job_description']}" class="dropdown-item p-2" target="_blank">
        <i class="fas fa-file mr-2"></i>
        View Job Description
      </a>`
    );
  }


  if (show_suspend_auto_approval) {
    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';
    const url = result['url'] + connector_char + 'suspend_auto_approval=1';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Suspend Auto Approval'),
      parent: 'moderator-admin-actions',
      title: gettext('Suspend *Auto Approval* of Bounty Hunters Who Have Applied for This Bounty')
    };

    actions.push(_entry);
  }

  if (show_admin_methods) {
    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';
    const url = result['url'] + connector_char + 'admin_override_and_hide=1';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Hide Bounty'),
      parent: 'moderator-admin-actions',
      title: gettext('Hides Bounty from Active Bounties')
    };

    actions.push(_entry);
  }

  if (show_admin_methods || show_moderator_methods) {
    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';

    let _entry = {
      enabled: true,
      href: result['url'] + connector_char + 'admin_toggle_as_remarket_ready=1',
      text: gettext('Toggle Remarket Ready'),
      parent: 'moderator-admin-actions',
      title: gettext('Sets Remarket Ready if not already remarket ready.  Unsets it if already remarket ready.')
    };

    actions.push(_entry);

    _entry = {
      enabled: true,
      href: '',
      text: gettext('Snooze Gitcoinbot'),
      parent: 'moderator-admin-actions',
      title: gettext('Snooze Gitcoinbot reminders')
    };
    actions.push(_entry);

    if (needs_review) {
      const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';
      const url = result['url'] + connector_char + 'mark_reviewed=1';

      const _entry = {
        enabled: true,
        href: url,
        text: gettext('Mark as Reviewed'),
        parent: 'moderator-admin-actions',
        title: gettext('Marks the bounty activity as reviewed.')
      };

      actions.push(_entry);
    }
  }

  if (show_admin_methods) {
    let _entry = {
      enabled: true,
      href: '',
      text: gettext('Override Status'),
      parent: 'moderator-admin-actions',
      title: gettext('Override Status with a status of your choosing'),
      buttonclass: 'admin_override_satatus'
    };

    actions.push(_entry);

    _entry = {
      enabled: true,
      href: '/_administrationdashboard/bounty/' + result['pk'] + '/change/',
      text: gettext('View in Admin'),
      parent: 'moderator-admin-actions',
      title: gettext('View in Admin')
    };
    actions.push(_entry);

    _entry = {
      enabled: true,
      href: '',
      text: gettext('Contact Funder'),
      parent: 'moderator-admin-actions',
      title: gettext('Contact Funder via Email'),
      buttonclass: 'contact_bounty_hunter'
    };

    actions.push(_entry);
  }

  $('#bounty-options-link').text().trim() == '' ? $('#bounty-options').hide() : $('#bounty-options').show();
  render_actions(actions);
};

const render_actions = function(actions) {
  for (let l = 0; l < actions.length; l++) {
    const target = actions[l]['parent'];
    const tmpl = $.templates('#action');
    const html = tmpl.render(actions[l]);

    let el = $(html).appendTo('#' + target);

    if (actions[l].clickhandler) {
      el.children('.button').click(actions[l].clickhandler);
    }
  }
};

const build_uri_for_pull_bounty_from_api = function() {
  let uri = '/actions/api/v0.1/bounties/?github_url=' + document.issueURL;

  if (typeof document.issueNetwork != 'undefined') {
    uri = uri + '&network=' + document.issueNetwork;
  }
  if (typeof document.issue_stdbounties_id != 'undefined') {
    uri = uri + '&standard_bounties_id=' + document.issue_stdbounties_id;
  }
  if (typeof document.eventTag != 'undefined') {
    uri = uri + '&event_tag=' + document.eventTag;
  }
  return uri;
};

var pull_bounty_from_api = function() {
  $.get(build_uri_for_pull_bounty_from_api()).then(results => {
    // special case: do not sanitize issue_description
    // before we pass it to the markdown parser
    return sanitizeAPIResults(results, 'issue_description');
  }).then(function(results) {
    let nonefound = true;
    // potentially make this a lot faster by only pulling the specific issue required

    for (let i = 0; i < results.length; i++) {
      var result = results[i];
      // if the result from the database matches the one in question.

      if (normalizeURL(result['github_url']) == normalizeURL(document.issueURL)) {
        nonefound = false;

        build_detail_page(result);

        do_actions(result);

        render_activity(result, results);

        document.result = result;

        if (document.result.event && localStorage['pendingProject'] && (document.result.standard_bounties_id == localStorage['pendingProject'])) {
          projectModal(document.result.pk);
        }

        return;
      }
    }
    if (nonefound) {
      $('#primary_view').css('display', 'none');
      // is there a pending issue or not?
      $('.nonefound').css('display', 'block');
    }
  }).fail(function(result) {
    console.log(result);
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'danger');
    $('#primary_view').css('display', 'none');
  }).always(function() {
    $('.loading').css('display', 'none');
  });
};


const process_activities = function(result, bounty_activities) {

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
    killed_bounty: gettext('Canceled Bounty'),
    new_crowdfund: gettext('Added new Crowdfund Contribution'),
    new_tip: gettext('Tip Sent'),
    receive_tip: gettext('Tip Received'),
    bounty_abandonment_escalation_to_mods: gettext('Escalated for Abandonment of Bounty'),
    bounty_abandonment_warning: gettext('Warned for Abandonment of Bounty'),
    bounty_removed_slashed_by_staff: gettext('Dinged and Removed from Bounty by Staff'),
    bounty_removed_by_staff: gettext('Removed from Bounty by Staff'),
    bounty_removed_by_funder: gettext('Removed from Bounty by Funder'),
    bounty_changed: gettext('Bounty Details Updated'),
    extend_expiration: gettext('Extended Bounty Expiration')
  };

  const now = result['now'] ? new Date(result['now']) : new Date();
  const is_open = result['is_open'];
  const _result = [];

  bounty_activities = bounty_activities || [];

  bounty_activities.forEach(function(_activity) {
    const type = _activity.activity_type;

    if (type === 'unknown_event' || type === 'receive_kudos') {
      return;
    }

    const meta = _activity.metadata || {};
    const fulfillment = meta.fulfillment || {};
    const new_bounty = meta.new_bounty || {};
    const old_bounty = meta.old_bounty || {};
    const issue_message = result.interested.length ?
      result.interested.find(interest => {
        if (interest.profile.handle === _activity.profile.handle && interest.issue_message) {
          return interest.issue_message;
        }
        return false;
      }) : false;
    const has_pending_interest = !!result.interested.find(interest =>
      interest.profile.handle === _activity.profile.handle && interest.pending);
    const has_interest = !!result.interested.find(interest =>
      interest.profile.handle === _activity.profile.handle);
    const slash_possible = currentProfile.isStaff;
    const is_logged_in = currentProfile.username;
    const uninterest_possible = is_logged_in && ((isBountyOwnerPerLogin(result) || currentProfile.isStaff) && is_open && has_interest);

    let profile_id = _activity.profile.id;
    let profile_handle = _activity.profile.handle;

    if (type === 'receive_tip') {
      // TODO: is not important for now, but maybe in the future?
      profile_id = 0;
      profile_handle = _activity.metadata.to_username;
    }

    let to_username = null;
    let kudos = null;
    let tip = null;
    let crowdfund = null;

    if (type === 'new_kudos') {
      to_username = meta.to_username.slice(1);
      if (!_activity.kudos) {
        return;
      }
      const kudos_img = _activity.kudos.image;

      kudos = kudos_img.startsWith('v2/images/') ? '/static/'.concat(kudos_img) : kudos_img;
    } else if (type == 'new_tip') {
      tip = {
        amount: meta.amount,
        token: meta.token_name,
        from: meta.from_name,
        to: meta.to_username
      };
    } else if (type == 'new_crowdfund') {
      crowdfund = {
        amount: meta.amount,
        token: meta.token_name,
        from: meta.from_name
      };
    }

    _result.push({
      profileId: profile_id,
      name: profile_handle,
      text: activity_names[_activity.activity_type],
      created_on: _activity.created,
      age: timeDifference(now, new Date(_activity.created)),
      activity_type: _activity.activity_type,
      status: _activity.activity_type === 'work_started' ? 'started' : 'stopped',
      issue_message: issue_message,
      uninterest_possible: uninterest_possible,
      slash_possible: slash_possible,
      approve_worker_url: meta.approve_worker_url,
      reject_worker_url: meta.reject_worker_url,
      worker_handle: meta.worker_handle,
      can_approve_worker: uninterest_possible && has_pending_interest,
      fulfiller_github_url: fulfillment.fulfiller_github_url,
      fulfillment_id: fulfillment.fulfillment_id,
      fulfiller_github_username: fulfillment.fulfiller_github_username,
      fulfiller_address: fulfillment.fulfiller_address,
      fulfillment_accepted: fulfillment.accepted,
      fulfillment_accepted_on: fulfillment.accepted_on,
      value_in_token_new: token_value_to_display(new_bounty.value_in_token),
      value_in_token_old: token_value_to_display(old_bounty.value_in_token),
      value_in_usdt_new: new_bounty.value_in_usdt_now,
      value_in_usdt_old: old_bounty.value_in_usdt_now,
      token_value_in_usdt_new: new_bounty.token_value_in_usdt,
      token_value_in_usdt_old: old_bounty.token_value_in_usdt,
      token_value_time_peg_new: new_bounty.token_value_time_peg,
      token_name: result['token_name'],
      to_username: to_username,
      kudos: kudos,
      permission_type: result['permission_type'],
      tip: tip,
      crowdfund: crowdfund
    });
  });

  return _result;
};

const only_one_approve = function(activities) {
  const seen = {};
  const iseen = {};

  for (let activity of activities) {
    if (activity.can_approve_worker) {
      if (!seen[activity.name]) {
        seen[activity.name] = true;
      } else {
        activity.can_approve_worker = false;
      }
    }
    if (activity.uninterest_possible) {
      if (activity.activity_type == 'bounty_abandonment_escalation_to_mods' || activity.activity_type == 'bounty_abandonment_escalation_to_mods') {
        // pass
      } else if (!iseen[activity.name]) {
        iseen[activity.name] = true;
      } else if (activity.activity_type != 'start_work') {
        activity.uninterest_possible = false;
        activity.slash_possible = false;
      }
    }
  }
};

const render_activity = function(result, all_results) {
  let all_activities = [];

  (all_results || []).forEach(result => {
    all_activities = all_activities.concat(result.activities);
  });

  let activities = process_activities(result, all_activities);

  activities = activities.slice().sort(function(a, b) {
    return a['created_on'] < b['created_on'] ? -1 : 1;
  }).reverse();
  only_one_approve(activities);

  var html = '<div class="row box activity"><div class="col-12 empty"><p>' + gettext('There\'s no activity yet!') + '</p></div></div>';

  if (activities.length > 0) {
    var template = $.templates('#activity_template');

    html = template.render(activities);
  }
  $('#activities').html(html);

  activities.filter(function(activity) {
    return activity.uninterest_possible;
  }).forEach(function(activity) {
    $('#remove-' + activity.name).on('click', function() {
      uninterested(result.pk, activity.profileId);
      return false;
    });
    $('#remove-slash-' + activity.name).on('click', function() {
      uninterested(result.pk, activity.profileId, true);
      return false;
    });
  });

};

const is_bounty_expired = function(bounty) {
  let expires_date = new Date(bounty['expires_date']);
  let now = new Date(bounty['now']);

  return now.getTime() >= expires_date.getTime();
};

/**
 * Checks sessionStorage to toggle to show the quote
 * container vs showing the list of fulfilled users to be
 * invite.
 */
const show_invite_users = () => {

  if (sessionStorage['fulfillers']) {
    const users = sessionStorage['fulfillers'].split(',');
    const bountyId = sessionStorage['bountyId'];

    if (users.length == 1) {

      let user = users[0];
      const title = `Work with <b>${user}</b> again on your next bounty ?`;
      const invite = `
        <div class="invite-user">
          <img class="avatar" src="/dynamic/avatar/${users}" />
          <p class="mt-4">
            <a target="_blank" class="btn btn-primary py-2 px-4" href="/users?invite=${user}&current-bounty=${bountyId}">
              Yes, invite to one of my bounties
            </a>
          </p>
        </div>`;

      $('#invite-header').html(title);
      $('#invite-users').html(invite);
    } else {

      let invites = [];
      const title = 'Work with these contributors again on your next bounty?';

      users.forEach(user => {
        const invite = `
          <div class="invite-user mx-3">
            <img class="avatar" src="/dynamic/avatar/${user}"/>
            <p class="my-2">
              <a target="_blank" class="font-subheader blue" href="/profile/${user}">
                ${user}
              </a>
            </p>
            <a target="_blank" class="btn btn-primary px-4 font-body font-weight-semibold" href="/users?invite=${user}&current-bounty=${bountyId}"">
              Invite
            </a>
          </div>`;

        invites.push(invite);
      });

      $('#invite-users').addClass('d-flex justify-content-center');
      $('#invite-header').html(title);
      $('#invite-users').html(invites);
    }
    $('.invite-user-container').removeClass('hidden');
    $('.quote-container').addClass('hidden');
  } else {
    $('.invite-user-container').addClass('hidden');
    $('.quote-container').removeClass('hidden');
  }
};

var main = function() {
  const moderatorAndAdminActions = $('#moderator-admin-actions');
  const scrollHeight = 150;

  $(window).scroll(RAFThrottle(() => {
    if (window.scrollY > scrollHeight) {
      moderatorAndAdminActions.addClass('sticky');
    } else {
      moderatorAndAdminActions.removeClass('sticky');
    }
  }));

  setTimeout(function() {
    // setup
    attach_work_actions();
    attach_contact_funder_options();
    attach_snoozee_options();
    attach_override_status();

    // pull issue URL
    if (typeof document.issueURL == 'undefined') {
      document.issueURL = getParam('url');
    }
    $('#submitsolicitation a').attr('href', '/funding/new/?source=' + document.issueURL);

    // if theres a pending submission for this issue, show the warning message
    // if not, pull the data from the API
    let isPending = false;

    if (localStorage[document.issueURL]) {
      // validate pending issue metadata
      document.pendingIssueMetadata = JSON.parse(localStorage[document.issueURL]);
      const is_metadata_valid = typeof document.pendingIssueMetadata != 'undefined' &&
        document.pendingIssueMetadata !== null &&
        typeof document.pendingIssueMetadata['timestamp'] != 'undefined';

      if (is_metadata_valid) {
        // validate that the pending tx is within the last little while
        const then = parseInt(document.pendingIssueMetadata['timestamp']);
        const now = timestamp();
        const acceptableTimeDeltaSeconds = 60 * 60; // 1 hour
        const isWithinAcceptableTimeRange = (now - then) < acceptableTimeDeltaSeconds;

        if (isWithinAcceptableTimeRange) {
          // update from web3
          const txid = document.pendingIssueMetadata.txid.transactionHash;

          showWarningMessage(txid);
          wait_for_tx_to_mine_and_then_ping_server();
          isPending = true;
        }
      }
    }
    // show the actual bounty page
    if (!isPending) {
      pull_bounty_from_api();
    }

  }, 100);
};

window.addEventListener('load', function() {
  main();
});
