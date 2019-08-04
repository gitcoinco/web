/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
// helper functions

/**
 *  * Generates a boostrap modal handler for when a user clicks a link to launch a boostrap modal.
 *   * @param {string} modalUrl - content url for the modal
 *    */
var show_modal_handler = (modalUrl) => {
	  const url = modalUrl;

	   return (e) => {
		       var modals = $('#modal');
		       var modalBody = $('#modal .modal-content');

	        modals.off('show.bs.modal');
		       modals.on('show.bs.modal', () => {
		         $('#modal .modal-content').load(modalUrl);
		       });
		       e.preventDefault();
		     };
};

/**
 * how many decimals are allowed in token displays
 */
let token_round_decimals = 3;

/**
 * Validates if input is a valid URL
 * @param {string} input - Input String
 */
var validURL = function(input) {
  var regex = /(([\w]+:)?\/\/)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,63}(:[\d]+)?(\/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?/;

  return regex.test(input);
};

/**
 * Looks for a transaction receipt.  If it doesn't find one, it keeps running until it does.
 * @callback
 * @param {string} txhash - The transaction hash.
 * @param {function} f - The function passed into this callback.
 */
var callFunctionWhenTransactionMined = function(txHash, f) {
  var transactionReceipt = web3.eth.getTransactionReceipt(txHash, function(error, result) {
    if (result) {
      f();
    } else {
      setTimeout(function() {
        callFunctionWhenTransactionMined(txHash, f);
      }, 1000);
    }
  });
};


/**
 * Looks for web3.  Won't call the fucntion until its there
 * @callback
 * @param {function} f - The function passed into this callback.
 */
var callFunctionWhenweb3Available = function(f) {
  if (typeof document.web3network != 'undefined') {
    f();
  } else {
    setTimeout(function() {
      callFunctionWhenweb3Available(f);
    }, 1000);
  }
};

var loading_button = function(button) {
  button.prop('disabled', true);
  button.prepend('<img src=' + static_url + 'v2/images/loading_white.gif style="max-width:20px; max-height: 20px">');
};

var update_metamask_conf_time_and_cost_estimate = function() {
  var confTime = 'unknown';
  var ethAmount = 'unknown';
  var usdAmount = 'unknown';

  var gasLimit = parseInt($('#gasLimit').val());
  var gasPrice = parseFloat($('#gasPrice').val());

  if (gasPrice) {
    var eth_amount_unrounded = gasLimit * gasPrice / Math.pow(10, 9);

    ethAmount = Math.round(1000000 * eth_amount_unrounded) / 1000000;
    usdAmount = Math.round(1000 * eth_amount_unrounded * document.eth_usd_conv_rate) / 1000;
  }

  if (typeof document.conf_time_spread == 'undefined') return;

  for (var i = 0; i < document.conf_time_spread.length - 1; i++) {
    var this_ele = (document.conf_time_spread[i]);
    var next_ele = (document.conf_time_spread[i + 1]);

    if (gasPrice <= parseFloat(next_ele[0]) && gasPrice > parseFloat(this_ele[0])) {
      confTime = Math.round(10 * next_ele[1]) / 10;
    }
  }

  $('#ethAmount').html(ethAmount);
  $('#usdAmount').html(usdAmount);
  $('#confTime').html(confTime);
};

var get_updated_metamask_conf_time_and_cost = function(gasPrice) {

  var confTime = 'unknown';
  var ethAmount = 'unknown';
  var usdAmount = 'unknown';

  var gasLimit = parseInt($('#gasLimit').val());

  if (gasPrice) {
    var eth_amount_unrounded = gasLimit * gasPrice / Math.pow(10, 9);

    ethAmount = Math.round(1000000 * eth_amount_unrounded) / 1000000;
    usdAmount = Math.round(100 * eth_amount_unrounded * document.eth_usd_conv_rate) / 100;
  }

  if (typeof document.conf_time_spread == 'undefined') return;

  for (var i = 0; i < document.conf_time_spread.length - 1; i++) {
    var this_ele = (document.conf_time_spread[i]);
    var next_ele = (document.conf_time_spread[i + 1]);

    if (gasPrice <= parseFloat(next_ele[0]) && gasPrice > parseFloat(this_ele[0])) {
      confTime = Math.round(10 * next_ele[1]) / 10;
    }
  }

  return {'eth': ethAmount, 'usd': usdAmount, 'time': confTime};
};

var unloading_button = function(button) {
  button.prop('disabled', false);
  button.removeClass('disabled');
  button.find('img').remove();
};

var sanitizeDict = function(d, keyToIgnore) {
  if (typeof d != 'object') {
    return d;
  }
  keys = Object.keys(d);
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];

    if (key === keyToIgnore) {
      continue;
    }

    d[key] = sanitize(d[key]);
  }
  return d;
};

var sanitizeAPIResults = function(results, keyToIgnore) {
  for (var i = 0; i < results.length; i++) {
    results[i] = sanitizeDict(results[i], keyToIgnore);
  }
  return results;
};

function ucwords(str) {
  return (str + '').replace(/^([a-z])|\s+([a-z])/g, function($1) {
    return $1.toUpperCase();
  });
}

var sanitize = function(str) {
  if (typeof str != 'string') {
    return str;
  }
  result = DOMPurify.sanitize(str);
  return result;
};

var getFormattedDate = function(date) {
  var monthNames = [
    'January', 'February', 'March',
    'April', 'May', 'June', 'July',
    'August', 'September', 'October',
    'November', 'December'
  ];

  var day = date.getDate();
  var monthIndex = date.getMonth();
  var year = date.getFullYear();

  return monthNames[monthIndex] + ' ' + day + ', ' + year;
};

var getTimeFromDate = function(date) {
  return date.getHours() + ':' + date.getMinutes();
};

var waitforWeb3 = function(callback) {
  if (document.web3network) {
    callback();
  } else {
    var wait_callback = function() {
      waitforWeb3(callback);
    };

    setTimeout(wait_callback, 100);
  }
};

var normalizeURL = function(url) {
  return url.replace(/\/$/, '');
};

var timestamp = function() {
  return Math.floor(Date.now() / 1000);
};


var showLoading = function() {
  $('.loading').css('display', 'flex');
  $('.nonefound').css('display', 'none');
  $('#primary_view').css('display', 'none');
  $('#actions').css('display', 'none');
  setTimeout(showLoading, 10);
};

var waitingStateActive = function() {
  $('.bg-container').show();
  $('.loading_img').addClass('waiting-state ');
  $('.waiting_room_entertainment').show();
  $('.issue-url').html('<a href="' + document.issueURL + '">' + document.issueURL + '</a>');
  waitingRoomEntertainment();
};

const notify_funder = (network, std_bounties_id, data) => {
  var request_url = '/actions/bounty/' + network + '/' + std_bounties_id + '/notify/funder_payout_reminder/';

  showBusyOverlay();
  $.post(request_url, data).then(() => {
    hideBusyOverlay();
    _alert({message: gettext('Sent payout reminder')}, 'success');
    $('#notifyFunder a').addClass('disabled');
    return true;
  }).fail(() => {
    hideBusyOverlay();
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'error');
  });
};

/** Add the current profile to the interested profiles list. */
var add_interest = function(bounty_pk, data) {
  if (document.interested) {
    return;
  }
  return mutate_interest(bounty_pk, 'new', data);
};

/** Remove the current profile from the interested profiles list. */
var remove_interest = function(bounty_pk, slash = false) {
  if (!document.interested) {
    return;
  }

  mutate_interest(bounty_pk, 'remove', slash);
};

/** Helper function -- mutates interests in either direction. */
var mutate_interest = function(bounty_pk, direction, data) {
  var request_url = '/actions/bounty/' + bounty_pk + '/interest/' + direction + '/';

  showBusyOverlay();
  return $.post(request_url, data).then(function(result) {
    hideBusyOverlay();

    result = sanitizeAPIResults(result);

    if (result.success) {
      if (direction === 'new') {
        _alert({ message: result.msg }, 'success');
        $('#interest a').attr('id', 'btn-white');
        return true;
      } else if (direction === 'remove') {
        _alert({ message: result.msg }, 'success');
        $('#interest a').attr('id', '');
      }

      pull_interest_list(bounty_pk);
      return true;
    }
    return false;
  }).fail(function(result) {
    hideBusyOverlay();

    var alertMsg = result && result.responseJSON ? result.responseJSON.error : null;

    if (alertMsg === null) {
      alertMsg = gettext('Network error. Please reload the page and try again.');
    }

    _alert({ message: alertMsg }, 'error');
  });
};


var uninterested = function(bounty_pk, profileId, slash) {
  var data = {};
  var success_message = 'Contributor removed from bounty.';

  if (slash) {
    success_message = 'Contributor removed from bounty and rep dinged';
    data.slashed = true;
  }

  var request_url = '/actions/bounty/' + bounty_pk + '/interest/' + profileId + '/uninterested/';

  showBusyOverlay();
  $.post(request_url, data, function(result) {
    hideBusyOverlay();

    result = sanitizeAPIResults(result);
    if (result.success) {
      _alert({ message: gettext(success_message) }, 'success');
      pull_interest_list(bounty_pk);
      return true;
    }
    return false;
  }).fail(function(result) {
    hideBusyOverlay();
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'error');
  });
};

var extend_expiration = function(bounty_pk, data) {
  var request_url = '/actions/bounty/' + bounty_pk + '/extend_expiration/';

  showBusyOverlay();
  $.post(request_url, data, function(result) {
    hideBusyOverlay();

    result = sanitizeAPIResults(result);
    if (result.success) {
      _alert({ message: result.msg }, 'success');
      pull_interest_list(bounty_pk);
      return true;
    }
    return false;
  }).fail(function(result) {
    hideBusyOverlay();
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'error');
  });
};


/** Pulls the list of interested profiles from the server. */
var pull_interest_list = function(bounty_pk, callback) {
  document.interested = false;
  var uri = '/actions/api/v0.1/bounties/?github_url=' + document.issueURL + '&not_current=1';
  var started = [];

  $.get(uri, function(results) {
    results = sanitizeAPIResults(results);
    const current = results.find(result => result.current_bounty);

    render_activity(current, results);
    if (current.interested) {
      var interested = current.interested;

      interested.forEach(function(_interested) {
        started.push(
          profileHtml(_interested.profile.handle)
        );
        if (_interested.profile.handle == document.contxt.github_handle) {
          document.interested = true;
        }
      });
    }
    if (started.length == 0) {
      started.push('<i class="fas fa-minus"></i>');
    }
    $('#started_owners_username').html(started);
    if (typeof callback != 'undefined') {
      callback(document.interested);
    }
  });
};

var profileHtml = function(handle, name) {
  return '<span><a href="https://gitcoin.co/profile/' +
    handle + '" target="_blank">' + (name ? name : handle) + '</span></a>';
};

// Update the list of bounty submitters.
var update_fulfiller_list = function(bounty_pk) {
  fulfillers = [];
  $.getJSON('/api/v0.1/bounties/' + bounty_pk, function(data) {
    data = sanitizeAPIResults(data);
    var fulfillmentList = data.fulfillments;

    $.each(fulfillmentList, function(index, value) {
      var fulfiller = value;

      fulfillers.push(fulfiller);
    });
    var tmpl = $.templates('#submitters');
    var html = tmpl.render(fulfillers);

    if (fulfillers.length == 0) {
      html = 'No one has submitted work yet.';
    }
    $('#submitter_list').html(html);
  });
  return fulfillers;
};

function validateEmail(email) {
  var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

  return re.test(email);
}

function getParam(parameterName) {
  var result = null;
  var tmp = [];

  location.search
    .substr(1)
    .split('&')
    .forEach(function(item) {
      tmp = item.split('=');
      if (tmp[0] === parameterName)
        result = decodeURIComponent(tmp[1]);
    });
  return result;
}

if ($.views) {
  $.views.converters({
    timedifference: timedifferenceCvrt,
    activitytext: activitytextCvrt
  });

}

function timedifferenceCvrt(date) {
  return timeDifference(new Date(), new Date(date), false, 60 * 60);
}

const activity_names = {
  new_bounty: gettext('New bounty'),
  start_work: gettext('Work started'),
  stop_work: gettext('Work stopped'),
  work_submitted: gettext('Work submitted'),
  work_done: gettext('Work done'),
  worker_approved: gettext('Worker approved'),
  worker_rejected: gettext('Worker rejected'),
  worker_applied: gettext('Worker applied'),
  increased_bounty: gettext('Increased funding'),
  killed_bounty: gettext('Canceled bounty'),
  new_crowdfund: gettext('New crowdfund contribution'),
  new_tip: gettext('New tip'),
  receive_tip: gettext('Tip received'),
  bounty_abandonment_escalation_to_mods: gettext('Escalated for abandonment of bounty'),
  bounty_abandonment_warning: gettext('Warned for abandonment of bounty'),
  bounty_removed_slashed_by_staff: gettext('Dinged and removed from bounty by staff'),
  bounty_removed_by_staff: gettext('Removed from bounty by staff'),
  bounty_removed_by_funder: gettext('Removed from bounty by funder'),
  bounty_changed: gettext('Bounty details changed')
};

function activitytextCvrt(activity_type) {
  return activity_names[activity_type];
}

function timeDifference(current, previous, remaining, now_threshold_seconds) {

  var elapsed = current - previous;

  if (now_threshold_seconds && (now_threshold_seconds * 1000) > Math.abs(elapsed)) {
    return 'now';
  }

  if (current < previous) {
    return 'in ' + timeDifference(previous, current).replace(' ago', '');
  }

  var msPerMinute = 60 * 1000;
  var msPerHour = msPerMinute * 60;
  var msPerDay = msPerHour * 24;
  var msPerMonth = msPerDay * 30;
  var msPerYear = msPerDay * 365;

  var amt;
  var unit;

  if (elapsed < msPerMinute) {
    amt = Math.round(elapsed / 1000);
    unit = 'second';
  } else if (elapsed < msPerHour) {
    amt = Math.round(elapsed / msPerMinute);
    unit = 'minute';
  } else if (elapsed < msPerDay) {
    amt = Math.round(elapsed / msPerHour);
    unit = 'hour';
  } else if (elapsed < msPerMonth) {
    amt = Math.round(elapsed / msPerDay);
    unit = 'day';
  } else if (elapsed < msPerYear) {
    amt = Math.round(elapsed / msPerMonth);
    unit = 'month';
  } else {
    amt = Math.round(elapsed / msPerYear);
    unit = 'year';
  }
  var plural = amt != 1 ? 's' : '';

  if (remaining) return amt + ' ' + unit + plural;
  return amt + ' ' + unit + plural + ' ago';
}

var attach_change_element_type = function() {
  (function($) {
    $.fn.changeElementType = function(newType) {
      var attrs = {};

      $.each(this[0].attributes, function(idx, attr) {
        attrs[attr.nodeName] = attr.nodeValue;
      });

      this.replaceWith(function() {
        return $('<' + newType + '/>', attrs).append($(this).contents());
      });
    };
  })(jQuery);
};

// callbacks that can retrieve various metadata about a github issue URL

var retrieveAmount = function() {
  var ele = $('input[name=amount]');
  var target_ele = $('#usd_amount');

  if (target_ele.html() == '') {
    target_ele.html('<img style="width: 50px; height: 50px;" src=' + static_url + 'v2/images/loading_v2.gif>');
  }

  var amount = $('input[name=amount]').val();
  var address = $('select[name=denomination]').val();
  var denomination = tokenAddressToDetails(address)['name'];
  var request_url = '/sync/get_amount?amount=' + amount + '&denomination=' + denomination;

  // use cached conv rate if possible.
  if (document.conversion_rates && document.conversion_rates[denomination]) {
    var usd_amount = amount / document.conversion_rates[denomination];

    updateAmountUI(target_ele, usd_amount);
    return;
  }

  // if not, use remote one
  $.get(request_url, function(result) {

    // update UI
    var usd_amount = result['usdt'];
    var conv_rate = amount / usd_amount;

    updateAmountUI(target_ele, usd_amount);

    // store conv rate for later in cache
    if (typeof document.conversion_rates == 'undefined') {
      document.conversion_rates = {};
    }
    document.conversion_rates[denomination] = conv_rate;

  }).fail(function() {
    target_ele.html(' ');
    // target_ele.html('Unable to find USDT amount');
  });
};

var updateAmountUI = function(target_ele, usd_amount) {
  usd_amount = Math.round(usd_amount * 100) / 100;

  if (usd_amount > 1000000) {
    usd_amount = Math.round(usd_amount / 100000) / 10 + 'm';
  } else if (usd_amount > 1000) {
    usd_amount = Math.round(usd_amount / 100) / 10 + 'k';
  }
  target_ele.html('Approx: ' + usd_amount + ' USD');
};

const showChoices = (choice_id, selector_id, choices) => {
  let html = '';
  let selected_choices = [];

  for (let i = 0; i < choices.length; i++) {
    html += '<li class="select2-available__choice">\
      <span class="select2-available__choice__remove" role="presentation">×</span>\
      <span class="text">' + choices[i] + '</span>\
      </li>';
  }
  $(choice_id).html(html);
  $('.select2-available__choice').on('click', function() {
    selected_choices.push($(this).find('.text').text());
    $(selector_id).val(selected_choices).trigger('change');
    $(this).remove();
  });
};

var retrieveIssueDetails = function() {
  var ele = $('input[name=issueURL]');
  var target_eles = {
    'title': $('input[name=title]'),
    'description': $('textarea[name=description]')
  };
  var issue_url = ele.val();

  if (typeof issue_url == 'undefined') {
    return;
  }
  if (issue_url.length < 5 || issue_url.indexOf('github') == -1) {
    return;
  }
  var request_url = '/sync/get_issue_details?url=' + encodeURIComponent(issue_url) + '&token=' + currentProfile.githubToken;

  $.each(target_eles, function(i, ele) {
    ele.addClass('loading');
  });
  $('#sync-issue').children('.fas').addClass('fa-spin');

  $.get(request_url, function(result) {
    result = sanitizeAPIResults(result);
    if (result['keywords']) {
      var keywords = result['keywords'];

      showChoices('#keyword-suggestions', '#keywords', keywords);
      $('#keywords').select2({
        placeholder: 'Select tags',
        data: keywords,
        tags: 'true',
        allowClear: true,
        tokenSeparators: [ ',', ' ' ]
      }).trigger('change');

    }
    target_eles['title'].val(result['title']);
    target_eles['description'].val(result['description']);
    $('#no-issue-banner').hide();
    $('#issue-details, #issue-details-edit').show();

    // $('#title--text').html(result['title']); // TODO: Refactor
    $.each(target_eles, function(i, ele) {
      ele.removeClass('loading');
    });
    $('#sync-issue').children('.fas').removeClass('fa-spin');

  }).fail(function() {
    $.each(target_eles, function(i, ele) {
      ele.removeClass('loading');
    });
  });
};


const randomElement = array => {
  const length = array.length;
  const randomNumber = Math.random();
  const randomIndex = Math.floor(randomNumber * length);

  return array[randomIndex];
};

/* eslint-disable no-lonely-if */
var currentNetwork = function(network) {

  $('.navbar-network').removeClass('hidden');
  let tooltip_info;

  document.web3network = network;
  if (document.location.href.startsWith('https://gitcoin.co')) { // Live
    if (network == 'mainnet') {
      $('#current-network').text('Main Ethereum Network');
      $('.navbar-network').attr('title', '');
      $('.navbar-network i').addClass('green');
      $('.navbar-network i').removeClass('red');
      $('#navbar-network-banner').removeClass('network-banner--warning');
      $('#navbar-network-banner').addClass('hidden');
    } else {
      if (!network) {
        info = gettext('Web3 disabled. Please install ') +
          '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>';
        $('#current-network').text(gettext('Metamask Not Enabled'));
        $('#navbar-network-banner').html(info);
      } else if (network == 'locked') {
        if (is_metamask_approved || !is_metamask_unlocked) {
          info = gettext('Web3 locked. Please unlock ') +
            '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>';
          $('#current-network').text(gettext('Metamask Locked'));
          $('#navbar-network-banner').html(info);
        } else {
          info = gettext('Metamask not connected. ') +
            '<button id="metamask_connect" onclick="approve_metamask()">Click here to connect to metamask</button>';
          $('#current-network').text(gettext('Metamask Not Connected'));
          $('#navbar-network-banner').html(info);
        }
      } else {
        info = gettext('Connect to Mainnet via Metamask');
        $('#current-network').text(gettext('Unsupported Network'));
        $('#navbar-network-banner').html(info);
      }

      $('.navbar-network i').addClass('red');
      $('.navbar-network i').removeClass('green');
      $('#navbar-network-banner').addClass('network-banner--warning');
      $('#navbar-network-banner').removeClass('hidden');

      if ($('.ui-tooltip.ui-corner-all.ui-widget-shadow.ui-widget.ui-widget-content').length == 0) {
        $('.navbar-network').attr('title', '<div class="tooltip-info tooltip-xs">' + info + '</div>');
      }
    }
  } else { // Staging
    if (network == 'rinkeby') {
      $('#current-network').text('Rinkeby Network');
      $('.navbar-network').attr('title', '');
      $('.navbar-network i').addClass('green');
      $('.navbar-network i').removeClass('red');
      $('#navbar-network-banner').removeClass('network-banner--warning');
      $('#navbar-network-banner').addClass('hidden');
    } else {
      if (!network) {
        info = gettext('Web3 disabled. Please install ') +
          '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>';
        $('#current-network').text(gettext('Metamask Not Enabled'));
        $('#navbar-network-banner').html(info);
      } else if (network == 'locked') {
        if (is_metamask_approved || !is_metamask_unlocked) {
          info = gettext('Web3 locked. Please unlock ') +
            '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>';
          $('#current-network').text(gettext('Metamask Locked'));
          $('#navbar-network-banner').html(info);
        } else {
          info = gettext('Metamask not connected. ') +
            '<button id="metamask_connect" onclick="approve_metamask()">Click here to connect to metamask</button>';
          $('#current-network').text(gettext('Metamask Not Connected'));
          $('#navbar-network-banner').html(info);
        }
      } else {
        info = gettext('Connect to Rinkeby / Custom RPC via Metamask');
        $('#current-network').text(gettext('Unsupported Network'));
        $('#navbar-network-banner').html(info);
      }

      $('.navbar-network i').addClass('red');
      $('.navbar-network i').removeClass('green');
      $('#navbar-network-banner').addClass('network-banner--warning');
      $('#navbar-network-banner').removeClass('hidden');

      if ($('.ui-tooltip.ui-corner-all.ui-widget-shadow.ui-widget.ui-widget-content').length == 0) {
        $('.navbar-network').attr('title', '<div class="tooltip-info tooltip-xs">' + info + '</div>');
      }
    }
  }
};
/* eslint-enable no-lonely-if */

/**
 * Throws custom alert based on user
 * - has not installed metamask
 * - metamask is locked
 * - metmask connection needs to be authorized
 * - logged in address has no ETH
 */
var trigger_primary_form_web3_hooks = function() {
  if ($('#primary_form').length) {
    var is_zero_balance_not_okay = document.location.href.indexOf('/faucet') == -1;

    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#primary_form, .primary_form-meta').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
    } else if (is_metamask_unlocked && !is_metamask_approved) {
      $('#connect_metamask_error').css('display', 'block');
      $('#unlock_metamask_error').css('display', 'none');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#primary_form, .primary_form-meta').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');
    } else if (!web3.eth.coinbase) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#primary_form, .primary_form-meta').addClass('hidden');
      $('#connect_metamask_error').css('display', 'none');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');
    } else if (is_zero_balance_not_okay && document.balance == 0) {
      $('#zero_balance_error').css('display', 'block');
      $('#robot_error').removeClass('hidden');
      $('#primary_form, .primary_form-meta').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
    } else {
      $('#zero_balance_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'block');
      $('#robot_error').addClass('hidden');
      $('#primary_form, .primary_form-meta').removeClass('hidden');
      $('.submit_bounty .newsletter').removeClass('hidden');
    }
  }
};


var trigger_faucet_form_web3_hooks = function() {
  var params = {};

  if ($('#faucet_form').length) {
    var balance = document.balance;

    $('#ethAddress').val(web3.eth.accounts[0]);
    var faucet_amount = parseInt($('#currentFaucet').val() * (Math.pow(10, 18)));

    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    } else if (is_metamask_unlocked && !is_metamask_approved) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'block');
      $('#over_balance_error').css('display', 'none');
      $('#faucet_form').addClass('hidden');
    } else if (!web3.eth.coinbase) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'block');
      $('#connect_metamask_error').css('display', 'none');
      $('#over_balance_error').css('display', 'none');
      $('#faucet_form').addClass('hidden');
      return;
    } else if (balance >= faucet_amount) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#over_balance_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
    } else {
      $('#over_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#faucet_form').removeClass('hidden');
    }
  }
  if ($('#admin_faucet_form').length || $('#admin_refund_form').length) {
    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    }
    if (is_metamask_unlocked && !is_metamask_approved) {
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
    }
    if (!web3.eth.coinbase) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    }
    web3.eth.getBalance(web3.eth.coinbase, function(errors, result) {
      if (errors) {
        return;
      }
      var balance = result.toNumber();

      if (balance == 0) {
        $('#zero_balance_error').css('display', 'block');
        $('#admin_faucet_form').remove();
      }
    });
  }
};

var trigger_form_hooks = function() {
  trigger_primary_form_web3_hooks();
  trigger_faucet_form_web3_hooks();
};

function getNetwork(id) {
  var networks = {
    '1': 'mainnet',
    '2': 'morden',
    '3': 'ropsten',
    '4': 'rinkeby',
    '42': 'kovan'
  };

  return networks[id] || 'custom network';
}

// figure out what version of web3 this is, whether we're logged in, etc..
var listen_for_web3_changes = async function() {

  if (document.location.pathname.indexOf('grants') === -1) {
    if (!document.listen_for_web3_iterations) {
      document.listen_for_web3_iterations = 1;
    } else {
      document.listen_for_web3_iterations += 1;
    }

    if (typeof web3 == 'undefined') {
      currentNetwork();
      trigger_form_hooks();
    } else if (typeof web3 == 'undefined' || typeof web3.eth == 'undefined' || typeof web3.eth.coinbase == 'undefined' || !web3.eth.coinbase) {
      currentNetwork('locked');
      trigger_form_hooks();
    } else {
      is_metamask_unlocked = true;
      web3.eth.getBalance(web3.eth.coinbase, function(errors, result) {
        if (errors) {
          return;
        }
        if (typeof result != 'undefined' && result !== null) {
          document.balance = result.toNumber();
        }
      });

      web3.version.getNetwork(function(error, netId) {
        if (error) {
          currentNetwork();
        } else {
          var network = getNetwork(netId);

          currentNetwork(network);
          trigger_form_hooks();
        }
      });
    }
  }

  if (window.ethereum && !document.has_checked_for_ethereum_enable && window.ethereum._metamask) {
    document.has_checked_for_ethereum_enable = true;
    is_metamask_approved = await window.ethereum._metamask.isApproved();
    is_metamask_unlocked = await window.ethereum._metamask.isUnlocked();
    if (is_metamask_approved && is_metamask_unlocked) {
      var start_time = ((new Date()).getTime() / 1000);

      await ethereum.enable();
      var now_time = ((new Date()).getTime() / 1000);
      var did_request_and_user_respond = (now_time - start_time) > 1.0;

      if (did_request_and_user_respond) {
        document.location.reload();
      }
    }
  }
};

var actions_page_warn_if_not_on_same_network = function() {
  var user_network = document.web3network;

  if (user_network === 'locked') {
    // handled by the unlock MetaMask banner
    return;
  }

  if (typeof user_network == 'undefined') {
    user_network = 'no network';
  }
  var bounty_network = $('input[name=network]').val();

  if (bounty_network != user_network) {
    var msg = 'Warning: You are on ' +
              user_network +
              ' and this bounty is on the ' +
              bounty_network +
              ' network.  Please change your network to the ' +
              bounty_network +
              ' network.';

    _alert({ message: gettext(msg) }, 'error');
  }
};

attach_change_element_type();

window.addEventListener('load', function() {
  setInterval(listen_for_web3_changes, 1000);
});

var callMethodIfTokenIsAuthed = function(success, failure) {
  var denomination = $('#token option:selected').text();
  var tokenAddress = $('#token option:selected').val();

  if (!denomination) {
    failure(denomination, tokenAddress);
  } else if (denomination == 'ETH') {
    success(denomination, tokenAddress);
  } else {
    var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
    var from = web3.eth.coinbase;
    var to = bounty_address();

    token_contract.allowance.call(from, to, function(error, result) {
      if (error || result.toNumber() == 0) {
        failure(denomination, tokenAddress);
      } else {
        success(denomination, tokenAddress);
      }
    });
  }
};

var promptForAuthFailure = function(denomination, tokenAddress) {
  _alert(
    gettext(`To enable this token, go to the
    <a style="padding-left:5px;" href="/settings/tokens">
    Token Settings page and enable it.
    </a> This is only needed once per token.`),
    'warning'
  );
};

var promptForAuth = function(event) {

  var success = function(denomination, tokenAddress) {
    $('.alert').remove();
  };

  callMethodIfTokenIsAuthed(success, promptForAuthFailure);
};

var setUsdAmount = function(event) {
  var amount = $('input[name=amount]').val();
  var denomination = $('#token option:selected').text();
  var estimate = getUSDEstimate(amount, denomination, function(estimate) {
    if (estimate['value']) {
      $('#usd-amount-wrapper').css('visibility', 'visible');
      $('#usd_amount_text').css('visibility', 'visible');

      $('#usd_amount').val(estimate['value_unrounded']);
      $('#usd_amount_text').html(estimate['rate_text']);
      $('#usd_amount').removeAttr('disabled');
    } else {
      $('#usd-amount-wrapper').css('visibility', 'hidden');
      $('#usd_amount_text').css('visibility', 'hidden');

      $('#usd_amount_text').html('');
      $('#usd_amount').prop('disabled', true);
      $('#usd_amount').val('');
    }
  });
};

var usdToAmount = function(event) {
  var usdAmount = $('input[name=usd_amount').val();
  var denomination = $('#token option:selected').text();
  var estimate = getAmountEstimate(usdAmount, denomination, function(amountEstimate) {
    if (amountEstimate['value']) {
      $('#amount').val(amountEstimate['value']);
      $('#usd_amount_text').html(amountEstimate['rate_text']);
    }
  });
};

function renderBountyRowsFromResults(results, renderForExplorer) {
  let html = '';
  const tmpl = $.templates('#result');

  if (results.length === 0) {
    return html;
  }

  for (var i = 0; i < results.length; i++) {
    const result = results[i];
    const relatedTokenDetails = tokenAddressToDetailsByNetwork(result['token_address'], result['network']);
    let decimals = 18;

    if (relatedTokenDetails && relatedTokenDetails.decimals) {
      decimals = relatedTokenDetails.decimals;
    }

    const divisor = Math.pow(10, decimals);

    result['rounded_amount'] = normalizeAmount(result['value_in_token'], decimals);

    const crowdfunding = result['additional_funding_summary'];

    if (crowdfunding) {
      const tokenDecimals = 3;
      const dollarDecimals = 2;
      const tokens = Object.keys(crowdfunding);
      let usdValue = 0.0;

      if (tokens.length) {
        const obj = {};

        while (tokens.length) {
          const tokenName = tokens.shift();
          const tokenObj = crowdfunding[tokenName];
          const amount = tokenObj['amount'];
          const ratio = tokenObj['ratio'];

          obj[tokenName] =
            normalizeAmount(amount, tokenDecimals);
          usdValue += amount * ratio;
        }
        result['tokens'] = obj;
      }

      if (usdValue && result['value_in_usdt']) {
        result['value_in_usdt'] =
          normalizeAmount(
            parseFloat(result['value_in_usdt']) + usdValue,
            dollarDecimals
          );
      }
    }

    const dateNow = new Date();
    const dateExpires = new Date(result['expires_date']);
    const isExpired = dateExpires < dateNow && !result['is_open'];
    const isInfinite = dateExpires - new Date().setFullYear(new Date().getFullYear() + 1) > 1;
    const projectType = ucwords(result['project_type']) + ' <span class="separator-bull"></span> ';

    result['action'] = result['url'];
    result['title'] = result['title'] ? result['title'] : result['github_url'];
    result['p'] = projectType + (result['experience_level'] ? (result['experience_level'] + ' <span class="separator-bull"></span> ') : '');
    result['expired'] = '';

    if (result['status'] === 'done') {
      result['p'] += 'Done';
      if (result['fulfillment_accepted_on']) {
        result['p'] += ' ' + timeDifference(dateNow, new Date(result['fulfillment_accepted_on']), false, 60 * 60);
      }
    } else if (result['status'] === 'started') {
      result['p'] += 'Started';
      if (result['fulfillment_started_on']) {
        result['p'] += ' ' + timeDifference(dateNow, new Date(result['fulfillment_started_on']), false, 60 * 60);
      }
    } else if (result['status'] === 'submitted') {
      result['p'] += 'Submitted';
      if (result['fulfillment_submitted_on']) {
        result['p'] += ' ' + timeDifference(dateNow, new Date(result['fulfillment_submitted_on']), false, 60 * 60);
      }
    } else if (result['status'] == 'cancelled') {
      result['p'] += 'Cancelled';
      if (result['canceled_on']) {
        result['p'] += ' ' + timeDifference(dateNow, new Date(result['canceled_on']), false, 60 * 60);
      }
    } else if (isExpired) {
      const timeAgo = timeDifference(dateNow, dateExpires, true);

      result['expired'] += ('Expired ' + timeAgo + ' ago');
    } else {
      const openedWhen = timeDifference(dateNow, new Date(result['web3_created']), true);

      if (isInfinite) {
        const expiredExpires = 'Never expires';

        result['p'] += ('Opened ' + openedWhen + ' ago');
        result['expired'] += (expiredExpires);
      } else {
        const timeLeft = timeDifference(dateNow, dateExpires);
        const expiredExpires = dateNow < dateExpires ? 'Expires' : 'Expired';

        result['p'] += ('Opened ' + openedWhen + ' ago');
        result['expired'] += (expiredExpires + ' ' + timeLeft);
      }
    }

    if (renderForExplorer) {
      if (typeof web3 != 'undefined' && typeof web3.eth != 'undefined' && web3.eth.coinbase == result['bounty_owner_address']) {
        result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">mine</span></a>';
      } else if (result['fulfiller_address'] !== '0x0000000000000000000000000000000000000000') {
        result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">' + result['status'] + '</span></a>';
      }

      result['watch'] = 'Watch';
    } else {
      result['hidden'] = (i > 4);
    }

    html += tmpl.render(result);
  }
  return html;
}

const saveAttestationData = (result, cost_eth, to_address, type) => {
  let request_url = '/revenue/attestations/new';
  let txid = result;
  let data = {
    'txid': txid,
    'amount': cost_eth,
    'network': document.web3network,
    'from_address': web3.eth.coinbase,
    'to_address': to_address,
    'type': type
  };

  $.post(request_url, data).then(function(result) {
    _alert('Success ✅ Loading your purchase now.', 'success');
  });
};

const renderFeaturedBountiesFromResults = (results, renderForExplorer) => {
  let html = '';
  const tmpl = $.templates('#featured-card');

  if (results.length === 0) {
    return html;
  }

  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    let decimals = 18;
    const relatedTokenDetails = tokenAddressToDetailsByNetwork(result['token_address'], result['network']);

    if (relatedTokenDetails && relatedTokenDetails.decimals) {
      decimals = relatedTokenDetails.decimals;
    }
    result['rounded_amount'] = normalizeAmount(result['value_in_token'], decimals);

    html += tmpl.render(result);
  }
  return html;
};

/**
 * Fetches results from the API and paints them onto the target element
 *
 * params - query params for bounty API
 * target - element
 * limit  - number of results
 *
 * TODO: refactor explorer to reuse this
 */
function fetchBountiesAndAddToList(params, target, limit, additional_callback) {
  $.get('/api/v0.1/bounties/?' + params, function(results) {
    results = sanitizeAPIResults(results);

    var html = renderBountyRowsFromResults(results);

    if (html) {
      $(target).prepend(html);
      $(target).removeClass('profile-bounties--loading');

      if (limit) {
        results = results.slice(0, limit);
      } else if (results.length > 5) {
        var $button = $(target + ' .profile-bounties__btn-show-all');

        $button.removeClass('hidden');
        $button.on('click', function(event) {
          $(this).remove();
          $(target + ' .bounty_row').removeClass('bounty_row--hidden');
        });
      }

      $('div.bounty_row.result').each(function() {
        var href = $(this).attr('href');

        if (typeof $(this).changeElementType !== 'undefined') {
          $(this).changeElementType('a');
        }
        $(this).attr('href', href);
      });
    } else {
      console.log($(target).parent().closest('.container').addClass('hidden'));
    }
    if (typeof additional_callback != 'undefined') {
      additional_callback(results);
    }
  });
}

function showBusyOverlay() {
  let overlay = document.querySelector('.busyOverlay');

  if (overlay) {
    overlay.style['display'] = 'block';
    overlay.style['animation-name'] = 'fadeIn';
    $(overlay).fadeIn('slow');
    return;
  }

  overlay = document.createElement('div');
  overlay.className = 'busyOverlay';
  overlay.addEventListener(
    'animationend',
    function() {
      if (overlay.style['animation-name'] === 'fadeOut') {
        overlay.style['display'] = 'none';
      }
    },
    false
  );
  document.body.appendChild(overlay);
}

function hideBusyOverlay() {
  let overlay = document.querySelector('.busyOverlay');

  if (overlay) {
    setTimeout(function() {
      $(overlay).fadeOut('slow');
      overlay.style['animation-name'] = 'fadeOut';
    }, 300);
  }
}

function toggleExpandableBounty(evt, selector) {
  evt.preventDefault();

  if (evt.target.id === 'expanded') {
    evt.target.id = '';
  } else {
    evt.target.id = 'expanded';
  }

  var container = document.body.querySelector(selector).querySelector('.expandable');

  if (container) {
    if (container.id === 'expanded') {
      container.id = '';
      evt.target.id = '';
      return;
    }
    container.id = 'expanded';
    evt.target.id = 'expanded';
  }
}

function normalizeAmount(amount, decimals) {
  return Math.round((parseInt(amount) / Math.pow(10, decimals)) * 1000) / 1000;
}

function round(amount, decimals) {
  return Math.round(((amount) * Math.pow(10, decimals))) / Math.pow(10, decimals);
}

function newTokenTag(amount, tokenName, tooltipInfo, isCrowdfunded) {
  const ele = document.createElement('div');
  const p = document.createElement('p');
  const span = document.createElement('span');

  ele.className = 'tag token';
  span.innerHTML = amount + ' ' + tokenName +
    (isCrowdfunded ? '<i class="fas fa-users ml-1"></i>' : '');

  p.appendChild(span);
  ele.appendChild(p);

  if (tooltipInfo) {
    ele.title =
      '<div class="tooltip-info tooltip-sm">' +
      tooltipInfo +
      '</div>';
  }

  return ele;
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));

    [ array[i], array[j] ] = [ array[j], array[i] ];
  }
  return array;
}

const getURLParams = (k) => {
  var p = {};

  location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(s, k, v) {
    p[k] = v;
  });
  return k ? p[k] : p;
};

const updateParams = (key, value) => {
  params = new URLSearchParams(window.location.search);
  if (params.get(key) === value) return;
  params.set(key, value);
  window.location.search = params.toString();
};

/**
 * shrinks text if it exceeds a given length which introduces a button
 * which can expand / shrink the text.
 * useage: <div class="more">...</div>
 *
 * @param {number} length - text length to be wrapped.
 */
const showMore = (length = 400) => {
  const placeholder = '...';
  const expand = 'More';
  const shrink = 'Less';

  $('.wrap-text').each(function() {
    const content = $(this).html();

    if (content.length > length) {
      const shortText = content.substr(0, length);
      const remainingText = content.substr(length, content.length - length + 1);
      const html = shortText + '<span class="moreellipses">' + placeholder +
      '&nbsp;</span><span class="morecontent"><span>' + remainingText +
      '</span>&nbsp;&nbsp;<a href="#" class="morelink">' + expand +
      '</a></span>';

      $(this).html(html);
    }
  });

  $('.morelink').on('click', function(event) {
    if ($(event.currentTarget).hasClass('less')) {
      $(event.currentTarget).removeClass('less');
      $(event.currentTarget).html(expand);
    } else {
      $(event.currentTarget).addClass('less');
      $(event.currentTarget).html(shrink);
    }
    $(event.currentTarget).parent().prev().toggle();
    $(event.currentTarget).prev().toggle();
    return false;
  });
};

/**
 * Check input file size
 *
 * input - input element
 * max_img_size  - max size
 *
 * Useage: checkFileSize($(input), 4000000)
 */
const checkFileSize = (input, max_img_size) => {
  if (input.files && input.files.length > 0) {
    if (input.files[0].size > max_img_size) {
      input.value = '';
      return false;
    }
  }
  return true;
};

/**
 * Compare two strings in a case insensitive way
 *
 * Usage: caseInsensitiveCompare('gitcoinco', 'GitcoinCo')
 */
const caseInsensitiveCompare = (val1, val2) => {
  if (val1 && val2 && typeof val1 === 'string' && typeof val2 === 'string') {
    return val1.toLowerCase() === val2.toLowerCase();
  }
  return false;
};

/**
 * A popup to notify users to approve metamask transaction
 * @param {*} closePopup [boolean]
 */
const indicateMetamaskPopup = (closePopup) => {
  if (closePopup) {
    $('#indicate-popup').hide();
  } else if ($('#indicate-popup').length) {
    if ($('#indicate-popup').is(':hidden')) {
      $('#indicate-popup').show();
    }
  } else {
    const svg = '<div id="indicate-popup"><svg width="214" height="165" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g fill="none" fill-rule="evenodd"><g transform="translate(47 25)"><rect fill="#0FCE7C" width="147" height="19" rx="3"/><text font-family="Muli" font-weight="bold" font-size="14" fill="#FFF"><tspan x="15.268" y="13">Web3 Action Pending</tspan></text></g><path d="M119.87 21.316l-5.69 4.714c-.463.383-.014.97 1.129.97h11.377c1.025 0 1.643-.545 1.13-.97l-5.688-4.714c-.506-.42-1.753-.422-2.258 0z" fill="#0FCE7C" fill-rule="nonzero"/><g transform="translate(0 7)"><rect fill="#FF7F00" width="214" height="158" rx="3"/><text font-family="Muli" font-size="14" fill="#FFF"><tspan x="17" y="23">Action Pending</tspan></text><text font-family="Muli" font-size="12" fill="#FFF"><tspan x="18" y="43">In order to use features of the </tspan> <tspan x="18" y="57">Gitcoin network we must </tspan> <tspan x="18" y="71">confirm transactions on the </tspan> <tspan x="18" y="85">ethereum blockchain.</tspan> <tspan x="18" y="127">Please check the pending </tspan> <tspan x="18" y="141">action on your secure wallet.</tspan></text></g><path d="M108.047.974l-7.316 7.071c-.594.575-.018 1.455 1.452 1.455h14.628c1.318 0 2.113-.818 1.452-1.455L110.95.974c-.65-.631-2.253-.633-2.903 0z" fill="#FF7F00" fill-rule="nonzero"/><path fill="#25E899" d="M181.747 30.054h13.298l1.127.422-.848 2.98h-12.74z"/><path d="M181.157 28.822h-.873c-.706 0-1.284-.568-1.284-1.261v-3.203c0-.694.578-1.262 1.284-1.262h.37" fill="#FFF"/><path d="M181.157 28.822h-.873c-.706 0-1.284-.568-1.284-1.261v-3.203c0-.694.578-1.262 1.284-1.262h.37" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/><path d="M196.781 28.822h.873c.706 0 1.284-.568 1.284-1.261v-3.203c0-.694-.578-1.262-1.284-1.262h-.37" fill="#FFF"/><path d="M196.781 28.822h.873c.706 0 1.284-.568 1.284-1.261v-3.203c0-.694-.578-1.262-1.284-1.262h-.37" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/><path d="M180.498 25.392c0-4.587 3.786-8.306 8.456-8.306s8.456 3.719 8.456 8.306l-2.086 8.065h-12.74l-2.086-8.065z" fill="#FFF"/><path d="M180.498 25.392c0-4.587 3.786-8.306 8.456-8.306s8.456 3.719 8.456 8.306l-2.086 8.065h-12.74l-2.086-8.065z" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/><path d="M193.523 37.14h-9.138c-.995 0-1.8-.791-1.8-1.768v-1.915h12.74v1.915c0 .977-.807 1.769-1.802 1.769" fill="#FFF"/><path d="M193.523 37.14h-9.138c-.995 0-1.8-.791-1.8-1.768v-1.915h12.74v1.915c0 .977-.807 1.769-1.802 1.769z" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/><path d="M186.618 30.054c-2-.863-3.396-2.826-3.396-5.109 0-1.347.486-2.583 1.296-3.547 1.041-1.24 7.593-1.302 8.633-.15a5.5 5.5 0 0 1 1.426 3.697c0 2.283-1.396 4.246-3.396 5.109" fill="#FF7F00"/><path d="M186.26 30.054c-1.98-.946-3.344-2.94-3.344-5.248a5.73 5.73 0 0 1 .934-3.14m9.794-.306a5.737 5.737 0 0 1 1.147 3.446c0 2.283-1.335 4.26-3.281 5.218m-11.012-4.752v-7.905m16.912 7.905V15.135" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/><path d="M180.59 24.002a11.945 11.945 0 0 1 8.498-3.541c3.138 0 5.996 1.21 8.136 3.192m-15.477 6.4h14.425" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/><path d="M191.922 23.097c0 .803-.664 1.454-1.481 1.454-.819 0-1.482-.65-1.482-1.454 0-.804.663-1.455 1.482-1.455.817 0 1.48.651 1.48 1.455m1.059 2.175a.593.593 0 0 1-.599.588.594.594 0 0 1-.599-.588c0-.325.268-.589.6-.589.33 0 .598.264.598.589" fill="#FFF"/><path d="M194.069 32.297c-.73 0-.73-1.084-1.46-1.084-.729 0-.729 1.084-1.459 1.084-.73 0-.73-1.084-1.46-1.084s-.73 1.084-1.46 1.084-.73-1.084-1.459-1.084c-.73 0-.73 1.084-1.46 1.084s-.73-1.084-1.461-1.084" stroke="#15003E" stroke-width="1.106" stroke-linecap="round"/></g></svg></div>';

    $('body').append(svg);
  }
};

$(document).ready(function() {
  $(window).scroll(function() {
    $('.g-fadein').each(function(i) {
      let duration = $(this).attr('data-fade-duration') ? $(this).attr('data-fade-duration') : 1500;
      let direction = $(this).attr('data-fade-direction') ? $(this).attr('data-fade-direction') : 'mid';
      let animateProps;

      switch (direction) {
        case 'left':
          animateProps = { 'opacity': '1', 'left': '0' };
          break;
        case 'right':
          animateProps = { 'opacity': '1', 'left': '0' };
          break;
        default:
          animateProps = { 'opacity': '1', 'bottom': '0' };
      }

      let bottom_of_object = $(this).position().top + $(this).outerHeight() / 2;
      let bottom_of_window = $(window).scrollTop() + $(window).height();

      if (bottom_of_window > bottom_of_object)
        $(this).animate(animateProps, duration);
    });
  });
});

function check_balance_and_alert_user_if_not_enough(
  tokenAddress,
  amount,
  msg = 'You do not have enough tokens to perform this action.') {

  if (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000') {
    return;
  }

  let token_contract = web3.eth.contract(token_abi).at(tokenAddress);
  let from = web3.eth.coinbase;
  let token_details = tokenAddressToDetails(tokenAddress);
  let token_decimals = token_details['decimals'];
  let token_name = token_details['name'];

  token_contract.balanceOf.call(from, function(error, result) {
    if (error) return;
    let balance = result.toNumber() / Math.pow(10, token_decimals);
    let balance_rounded = Math.round(balance * 10) / 10;

    if (parseFloat(amount) > balance) {
      let msg1 = gettext(msg);
      let msg2 = gettext(' You have ') + balance_rounded + ' ' + token_name + ' ' + gettext(' but you need ') + amount + ' ' + token_name;

      _alert(msg1 + msg2, 'warning');
    }
  });

}
