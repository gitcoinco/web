/* eslint block-scoped-var: "warn" */
/* eslint no-redeclare: "warn" */


var _truthy = function(val) {
  if (!val || val == '0x0000000000000000000000000000000000000000') {
    return false;
  }
  return true;
};
var address_ize = function(key, val, result) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="https://etherscan.io/address/' + val + '" target="_blank" rel="noopener noreferrer">' + val + '</a>' ];
};
var gitcoin_ize = function(key, val, result) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="https://gitcoin.co/profile/' + val + '" target="_blank" rel="noopener noreferrer">@' + val.replace('@', '') + '</a>' ];
};
var email_ize = function(key, val, result) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, '<a href="mailto:' + val + '">' + val + '</a>' ];
};
var hide_if_empty = function(key, val, result) {
  if (!_truthy(val)) {
    return [ null, null ];
  }
  return [ key, val ];
};
var unknown_if_empty = function(key, val, result) {
  if (!_truthy(val)) {
    $('#' + key).parent().hide();
    return [ key, 'Unknown' ];
  }
  return [ key, val ];
};
var link_ize = function(key, val, result) {
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
  'github_url',
  'value_in_token',
  'value_in_eth',
  'value_in_usdt',
  'token_value_in_usdt',
  'token_value_time_peg',
  'web3_created',
  'status',
  'project_type',
  'permission_type',
  'bounty_owner_address',
  'bounty_owner_email',
  'issue_description',
  'bounty_owner_github_username',
  'fulfillments',
  'network',
  'experience_level',
  'project_length',
  'bounty_type',
  'expires_date',
  'bounty_owner_name',
  'issue_keywords',
  'started_owners_username',
  'submitted_owners_username',
  'fulfilled_owners_username',
  'fulfillment_accepted_on'
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
    return [ 'amount', token_value_to_display(val) + ' ' + result['token_name'] ];
  },
  'avatar_url': function(key, val, result) {
    return [ 'avatar', '<a href="/profile/' + result['org_name'] + '"><img class=avatar src="' + val + '"></a>' ];
  },
  'issuer_avatar_url': function(key, val, result) {
    var username = result['bounty_owner_github_username'] ? result['bounty_owner_github_username'] : 'Self';

    return [ 'issuer_avatar_url', '<a href="/profile/' + result['bounty_owner_github_username'] +
      '"><img class=avatar src="/funding/avatar?repo=https://github.com/' + username + '"></a>' ];
  },
  'status': function(key, val, result) {
    var ui_status = val;

    if (ui_status == 'open') {
      ui_status = '<span>' + gettext('OPEN ISSUE') + '</span>';
    }
    if (ui_status == 'started') {
      ui_status = '<span>' + gettext('work started') + '</span>';
    }
    if (ui_status == 'submitted') {
      ui_status = '<span>' + gettext('work submitted') + '</span>';
    }
    if (ui_status == 'done') {
      ui_status = '<span>' + gettext('done') + '</span>';
    }
    if (ui_status == 'cancelled') {
      ui_status = '<span style="color: #f9006c;">' + gettext('cancelled') + '</span>';
    }
    return [ 'status', ui_status ];
  },
  'issue_description': function(key, val, result) {
    var converter = new showdown.Converter();

    ui_body = converter.makeHtml(val);
    return [ 'issue_description', ui_body ];
  },
  'bounty_owner_address': address_ize,
  'bounty_owner_email': email_ize,
  'experience_level': unknown_if_empty,
  'project_length': unknown_if_empty,
  'bounty_type': unknown_if_empty,
  'bounty_owner_github_username': gitcoin_ize,
  'bounty_owner_name': function(key, val, result) {
    return [ 'bounty_owner_name', result.bounty_owner_name ];
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
  'issue_keywords': function(key, val, result) {
    if (!result.keywords || result.keywords.length == 0)
      return [ 'issue_keywords', null ];

    var keywords = result.keywords.split(',');
    var tags = [];

    keywords.forEach(function(keyword) {
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
    var rates_estimate = get_rates_estimate(val);

    $('#value_in_usdt_wrapper').attr('title', '<div class="tooltip-info tooltip-sm">' + rates_estimate + '</div>');

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
    if (val == 'mainnet') {
      $('#network').addClass('hidden');
      return [ null, null ];
    }
    var warning = 'WARNING: this is a ' + val + ' network bounty, and is NOT real money.  To see mainnet bounties, go to <a href="/explorer">the bounty explorer</a> and search for mainnet bounties.  ';

    return [ 'network', warning ];
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
    var label = 'expires';

    expires_date = new Date(val);
    now = new Date(result['now']);

    var expiringInPercentage = 100 * (
      (now.getTime() - new Date(result['web3_created']).getTime()) /
      (expires_date.getTime() - new Date(result['web3_created']).getTime()));

    if (expiringInPercentage > 100) {
      expiringInPercentage = 100;
    }

    $('.progress').css('width', expiringInPercentage + '%');
    var response = timeDifference(now, expires_date).split(' ');

    if (expires_date < new Date()) {
      label = 'expired';
      if (result['is_open']) {
        var soft = result['can_submit_after_expiration_date'] ? 'Soft ' : '';

        $('.timeleft').text(soft + 'Expired');
        $('.progress-bar').addClass('expired');
        response = '<span title="This issue is past its expiration date, but it is still active.  Check with the submitter to see if they still want to see it fulfilled.">' + response.join(' ') + '</span>';
      } else {
        $('#timer').hide();
      }
    } else if (result['status'] === 'done' || result['status'] === 'cancelled') {
      $('#timer').hide();
    } else {
      response.shift();
      response = response.join(' ');
    }
    return [ label, response ];
  },
  'started_owners_username': function(key, val, result) {
    var started = [];

    if (result.interested) {
      var interested = result.interested;

      interested.forEach(function(_interested, position) {
        var name = (position == interested.length - 1) ?
          _interested.profile.handle : _interested.profile.handle.concat(',');

        started.push(profileHtml(_interested.profile.handle, name));
      });
      if (started.length == 0) {
        started.push('<i class="fas fa-minus"></i>');
      }
    }
    return [ 'started_owners_username', started ];
  },
  'submitted_owners_username': function(key, val, result) {
    var accepted = [];

    if (result.fulfillments) {
      var submitted = result.fulfillments;

      submitted.forEach(function(_submitted, position) {
        var name = (position == submitted.length - 1) ?
          _submitted.fulfiller_github_username : _submitted.fulfiller_github_username.concat(',');

        accepted.push(profileHtml(_submitted.fulfiller_github_username, name));
      });
      if (accepted.length == 0) {
        accepted.push('<i class="fas fa-minus"></i>');
      }
    }
    return [ 'submitted_owners_username', accepted ];
  },
  'fulfilled_owners_username': function(key, val, result) {
    var accepted = [];
    var accepted_fufillments = [];

    if (result.fulfillments) {
      var fulfillments = result.fulfillments;

      fulfillments.forEach(function(fufillment) {
        if (fufillment.accepted == true)
          accepted_fufillments.push(fufillment.fulfiller_github_username);
      });
      if (accepted_fufillments.length == 0) {
        accepted.push('<i class="fas fa-minus"></i>');
      } else {
        accepted_fufillments.forEach((github_username, position) => {
          var name = (position == accepted_fufillments.length - 1) ?
            github_username : github_username.concat(',');

          accepted.push(profileHtml(github_username, name));
        });
      }
    }
    return [ 'fulfilled_owners_username', accepted ];
  }
};

var isBountyOwner = function(result) {
  var bountyAddress = result['bounty_owner_address'];

  if (typeof web3 == 'undefined') {
    return false;
  }
  if (typeof web3.eth.coinbase == 'undefined' || !web3.eth.coinbase) {
    return false;
  }

  return (web3.eth.coinbase.toLowerCase() == bountyAddress.toLowerCase());
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

  update_title();
  $('.interior .body').addClass('open');
  $('.interior .body').addClass('loading');

  if (typeof txid != 'undefined' && txid.indexOf('0x') != -1) {
    clearInterval(interval);
    var link_url = etherscan_tx_url(txid);

    $('#transaction_url').attr('href', link_url);
  }

  $('.left-rails').hide();
  $('#bounty_details').hide();
  $('#bounty_detail').hide();

  $('.bg-container').show();
  $('.loading_img').addClass('waiting-state ');
  $('.waiting_room_entertainment').show();
  $('.issue-url').html('<a href="' + document.issueURL + '">' + document.issueURL + '</a>');

  var secondsBetweenQuoteChanges = 30;

  waitingRoomEntertainment();
  var interval = setInterval(waitingRoomEntertainment, secondsBetweenQuoteChanges * 1000);
};

var wait_for_tx_to_mine_and_then_ping_server = function() {
  console.log('checking for updates');
  if (typeof document.pendingIssueMetadata != 'undefined') {
    var txid = document.pendingIssueMetadata['txid'];

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
          document.location.href = document.location.href;
        };
        var success = function(response) {
          if (response.status == '200') {
            console.log('success from sync/web', response);

            // clear local data
            localStorage[document.issueURL] = '';
            if (response['url']) {
              document.location.href = response['url'];
            } else {
              document.location.href = document.location.href;
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
  $('body').delegate('a[href="/interested"], a[href="/uninterested"]', 'click', function(e) {
    e.preventDefault();
    if ($(this).attr('href') == '/interested') {
      show_interest_modal.call(this);
    } else if (confirm(gettext('Are you sure you want to stop work?'))) {
      $(this).attr('href', '/interested');
      $(this).find('span').text(gettext('Start Work'));
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


var show_interest_modal = function() {
  var self = this;

  setTimeout(function() {
    var url = '/interest/modal?redirect=' + window.location.pathname + '&pk=' + document.result['pk'];

    $.get(url, function(newHTML) {
      var modal = $(newHTML).appendTo('body').modal({
        modalClass: 'modal add-interest-modal'
      });

      modal.on('submit', function(event) {
        event.preventDefault();

        var issue_message = event.target[0].value.trim();
        var agree_precedence = event.target[1].checked;
        var agree_not_to_abandon = event.target[2].checked;

        if (!issue_message) {
          _alert({message: gettext('Please provide an action plan for this ticket.')}, 'error');
          return false;
        }

        if (!agree_precedence) {
          _alert({message: gettext('You must agree to the precedence clause.')}, 'error');
          return false;
        }
        if (!agree_not_to_abandon) {
          _alert({message: gettext('You must agree to keep the funder updated on your progress.')}, 'error');
          return false;
        }

        $(self).attr('href', '/uninterested');
        $(self).find('span').text(gettext('Stop Work'));
        add_interest(document.result['pk'], {
          issue_message
        });
        $.modal.close();
      });
    });
  });
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
    var _entry = {
      'head': head,
      'key': key,
      'val': val
    };
    var id = '#' + key;

    if ($(id).length) {
      $(id).html(val);
    }
  }

  $('#bounty_details #issue_description img').on('click', function() {

    var content = $.parseHTML(
      '<div><div class="row"><div class="col-12 closebtn">' +
        '<a id="" rel="modal:close" href="javascript:void" class="close" aria-label="Close dialog">' +
          '<span aria-hidden="true">&times;</span>' +
        '</a>' +
      '</div>' +
      '<div class="col-12 pt-2 pb-2"><img class="magnify" src="' + $(this).attr('src') + '"/></div></div></div>');

    var modal = $(content).appendTo('body').modal({
      modalClass: 'modal magnify'
    });
  });
};

const is_current_user_interested = function(result) {
  return !!(result.interested || []).find(interest => interest.profile.handle == document.contxt.github_handle);
};

var do_actions = function(result) {
  // helper vars
  var is_legacy = result['web3_type'] == 'legacy_gitcoin';
  // var is_date_expired = (new Date(result['now']) > new Date(result['expires_date']));
  var is_status_expired = result['status'] == 'expired';
  var is_status_done = result['status'] == 'done';
  var is_status_cancelled = result['status'] == 'cancelled';
  var can_submit_after_expiration_date = result['can_submit_after_expiration_date'];
  var is_still_on_happy_path = result['status'] == 'open' || result['status'] == 'started' || result['status'] == 'submitted' || (can_submit_after_expiration_date && result['status'] == 'expired');
  const is_open = result['is_open'];

  // Find interest information
  const is_interested = is_current_user_interested(result);

  document.interested = is_interested;

  // which actions should we show?
  const should_block_from_starting_work = !is_interested && result['project_type'] == 'traditional' && (result['status'] == 'started' || result['status'] == 'submitted');
  let show_start_stop_work = is_still_on_happy_path && !should_block_from_starting_work && is_open;
  let show_github_link = result['github_url'].substring(0, 4) == 'http';
  let show_submit_work = is_open;
  let show_kill_bounty = !is_status_done && !is_status_expired && !is_status_cancelled;
  let show_job_description = result['attached_job_description'] && result['attached_job_description'].startsWith('http');
  const show_increase_bounty = !is_status_done && !is_status_expired && !is_status_cancelled;
  const kill_bounty_enabled = isBountyOwner(result);
  const submit_work_enabled = !isBountyOwner(result);
  const start_stop_work_enabled = !isBountyOwner(result);
  const increase_bounty_enabled = isBountyOwner(result);
  let show_accept_submission = isBountyOwner(result) && !is_status_expired && !is_status_done;
  let show_advanced_payout = isBountyOwner(result) && !is_status_expired && !is_status_done;
  const show_suspend_auto_approval = document.isStaff && result['permission_type'] == 'approval';
  const show_admin_methods = document.isStaff;

  if (is_legacy) {
    show_start_stop_work = false;
    show_github_link = true;
    show_submit_work = false;
    show_kill_bounty = false;
    show_accept_submission = false;
  }

  // actions
  const actions = [];

  if (show_submit_work) {
    const enabled = submit_work_enabled;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['fulfill'],
      text: gettext('Submit Work'),
      parent: 'right_actions',
      title: gettext('Submit work for the funder to review'),
      work_started: is_interested,
      id: 'submit'
    };

    actions.push(_entry);
  }

  if (show_start_stop_work) {
    const enabled = start_stop_work_enabled;
    const interest_entry = {
      enabled: enabled,
      href: is_interested ? '/uninterested' : '/interested',
      text: is_interested ? gettext('Stop Work') : gettext('Start Work'),
      parent: 'right_actions',
      title: is_interested ? gettext('Notify the funder that you will not be working on this project') : gettext('Notify the funder that you would like to take on this project'),
      color: is_interested ? 'white' : '',
      id: 'interest'
    };

    actions.push(interest_entry);
  }

  if (show_kill_bounty) {
    const enabled = kill_bounty_enabled;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['cancel'],
      text: gettext('Cancel Bounty'),
      parent: 'right_actions',
      title: gettext('Cancel bounty and reclaim funds for this issue')
    };

    actions.push(_entry);
  }

  const pending_acceptance = result.fulfillments.filter(fulfillment => fulfillment.accepted == false).length;

  if (show_accept_submission && pending_acceptance > 0) {
    const enabled = show_accept_submission;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['accept'],
      text: gettext('Accept Submission'),
      title: gettext('This will payout the bounty to the submitter.'),
      parent: 'right_actions',
      pending_acceptance: pending_acceptance
    };

    actions.push(_entry);
  }

  if (show_job_description) {
    var job_url = result['attached_job_description'];

    var _entry = {
      enabled: true,
      href: job_url,
      text: gettext('View Attached Job Description'),
      parent: 'right_actions',
      title: gettext('This bounty hunter is hiring for a full time, part time, or contract role and has attached that to this bounty.'),
      color: 'white'
    };

    actions.push(_entry);
  }


  if (show_advanced_payout) {
    const enabled = show_advanced_payout;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['payout'],
      text: gettext('Multi-Party Payout'),
      title: gettext('Used to pay out to many people at once.'),
      parent: 'right_actions',
      pending_acceptance: pending_acceptance
    };

    actions.push(_entry);
  }

  if (show_increase_bounty) {
    const enabled = increase_bounty_enabled;
    const _entry = {
      enabled: enabled,
      href: result['action_urls']['increase'],
      text: gettext('Add Contribution'),
      parent: 'right_actions',
      title: gettext('Increase the funding for this issue')
    };

    actions.push(_entry);
  }

  if (show_github_link) {
    let github_url = result['github_url'];
    // hack to get around the renamed repo for piper's work.  can't change the data layer since blockchain is immutable

    github_url = github_url.replace('pipermerriam/web3.py', 'ethereum/web3.py');
    github_url = github_url.replace('ethereum/browser-solidity', 'ethereum/remix-ide');

    const _entry = {
      enabled: true,
      href: github_url,
      text: gettext('View On Github'),
      parent: 'right_actions',
      title: gettext('View issue details and comments on Github'),
      comments: result['github_comments'],
      color: 'white',
      is_last_non_admin_action: true
    };

    actions.push(_entry);
  }
  if (show_suspend_auto_approval) {
    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';
    const url = result['url'] + connector_char + 'suspend_auto_approval=1';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Suspend Auto Approval'),
      parent: 'right_actions',
      title: gettext('Suspend *Auto Approval* of Bounty Hunters Who Have Applied for This Bounty'),
      color: 'white',
      buttonclass: 'admin-only'
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
      parent: 'right_actions',
      title: gettext('Hides Bounty from Active Bounties'),
      color: 'white',
      buttonclass: 'admin-only'
    };

    actions.push(_entry);
  }

  if (show_admin_methods) {
    const connector_char = result['url'].indexOf('?') == -1 ? '?' : '&';
    const url = result['url'] + connector_char + 'admin_toggle_as_remarket_ready=1';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Toggle Remarket Ready'),
      parent: 'right_actions',
      title: gettext('Sets Remarket Ready if not already remarket ready.  Unsets it if already remarket ready.'),
      color: 'white',
      buttonclass: 'admin-only'
    };

    actions.push(_entry);
  }

  if (show_admin_methods) {
    const url = '';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Contact Funder'),
      parent: 'right_actions',
      title: gettext('Contact Funder via Email'),
      color: 'white',
      buttonclass: 'admin-only contact_bounty_hunter'
    };

    actions.push(_entry);
  }

  if (show_admin_methods) {
    const url = '';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Snooze Gitcoinbot'),
      parent: 'right_actions',
      title: gettext('Snooze Gitcoinbot reminders'),
      color: 'white',
      buttonclass: 'admin-only snooze_gitcoin_bot'
    };

    actions.push(_entry);
  }

  if (show_admin_methods) {
    const url = '';

    const _entry = {
      enabled: true,
      href: url,
      text: gettext('Override Status'),
      parent: 'right_actions',
      title: gettext('Override Status with a status of your choosing'),
      color: 'white',
      buttonclass: 'admin-only admin_override_satatus'
    };

    actions.push(_entry);
  }

  render_actions(actions);
};

const render_actions = function(actions) {
  for (let l = 0; l < actions.length; l++) {
    const target = actions[l]['parent'];
    const tmpl = $.templates('#action');
    const html = tmpl.render(actions[l]);

    $('#' + target).append(html);
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
  return uri;
};

var pull_bounty_from_api = function() {
  let all_results = [];

  $.get(build_uri_for_pull_bounty_from_api()).then(results => {
    all_results = sanitizeAPIResults(results);
    return all_results;
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

        render_activity(result, all_results);

        document.result = result;
        return;
      }
    }
    if (nonefound) {
      $('#primary_view').css('display', 'none');
      // is there a pending issue or not?
      $('.nonefound').css('display', 'block');
    }
  }).fail(function() {
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'error');
    $('#primary_view').css('display', 'none');
  }).always(function() {
    $('.loading').css('display', 'none');
  });
};


const process_activities = function(result, bounty_activities) {
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
    new_tip: gettext('New Tip'),
    receive_tip: gettext('Tip Received')
  };

  const now = new Date(result['now']);
  const is_open = result['is_open'];

  return (bounty_activities || []).map(function(_activity) {
    const meta = _activity.metadata || {};
    const fulfillment = meta.fulfillment || {};
    const new_bounty = meta.new_bounty || {};
    const old_bounty = meta.old_bounty || {};
    const uninterest_possible = (isBountyOwner(result) || document.isStaff) && is_open;
    const has_pending_interest = !!result.interested.find(interest =>
      interest.profile.handle === _activity.profile.handle && interest.pending);
    const has_interest = !!result.interested.find(interest =>
      interest.profile.handle === _activity.profile.handle);

    return {
      profileId: _activity.profile.id,
      name: _activity.profile.handle,
      text: activity_names[_activity.activity_type],
      created_on: _activity.created,
      age: timeDifference(now, new Date(_activity.created)),
      activity_type: _activity.activity_type,
      status: _activity.activity_type === 'work_started' ? 'started' : 'stopped',
      uninterest_possible: uninterest_possible && has_interest,
      slash_possible: document.isStaff && has_interest,
      approve_worker_url: meta.approve_worker_url,
      reject_worker_url: meta.reject_worker_url,
      worker_handle: meta.worker_handle,
      can_approve_worker: uninterest_possible && has_pending_interest,
      fulfiller_github_url: fulfillment.fulfiller_github_url,
      fulfillment_id: fulfillment.fulfillment_id,
      fulfiller_github_username: fulfillment.fulfiller_github_username,
      fulfiller_email: fulfillment.fulfiller_email,
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
      token_name: result['token_name']
    };
  });
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
      if (!iseen[activity.name]) {
        iseen[activity.name] = true;
      } else {
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
    $('#remove-' + activity.name).click(() => {
      uninterested(result.pk, activity.profileId);
      return false;
    });
    $('#remove-slash-' + activity.name).click(() => {
      uninterested(result.pk, activity.profileId, true);
      return false;
    });
  });

};

var main = function() {
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
    var isPending = false;

    if (localStorage[document.issueURL]) {
      // validate pending issue metadata
      document.pendingIssueMetadata = JSON.parse(localStorage[document.issueURL]);
      var is_metadata_valid = typeof document.pendingIssueMetadata != 'undefined' && document.pendingIssueMetadata !== null && typeof document.pendingIssueMetadata['timestamp'] != 'undefined';

      if (is_metadata_valid) {
        // validate that the pending tx is within the last little while
        var then = parseInt(document.pendingIssueMetadata['timestamp']);
        var now = timestamp();
        var acceptableTimeDeltaSeconds = 60 * 60; // 1 hour
        var isWithinAcceptableTimeRange = (now - then) < acceptableTimeDeltaSeconds;

        if (isWithinAcceptableTimeRange) {
          // update from web3
          var txid = document.pendingIssueMetadata['txid'];

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
