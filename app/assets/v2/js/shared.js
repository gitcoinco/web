/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
// helper functions

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
  button.addClass('disabled');
  button.prepend('<img src=' + static_url + 'v2/images/loading_white.gif style="max-width:20px; max-height: 20px">').addClass('disabled');
};

var attach_close_button = function() {
  $('body').delegate('.alert .closebtn', 'click', function(e) {
    $(this).parents('.alert').remove();
    $('.alert').each(function(index) {
      if (index == 0) $(this).css('top', 0);
      else {
        var new_top = (index * 66) + 'px';

        $(this).css('top', new_top);
      }
    });
  });
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

var _alert = function(msg, _class) {
  if (typeof msg == 'string') {
    msg = {
      'message': msg
    };
  }
  var numAlertsAlready = $('.alert:visible').length;
  var top = numAlertsAlready * 66;

  var html = function() {
    return (
      `<div class="alert ${_class} g-font-muli" style="top: ${top}px">
        <div class="message">
          <div class="content">
            ${alertMessage(msg)}
          </div>
        </div>
        ${closeButton(msg)}
      </div>`
    );
  };

  $('body').append(html);
};

var closeButton = function(msg) {
  var html = (msg['closeButton'] === false ? '' : '<span class="closebtn" >&times;</span>');

  return html;
};

var alertMessage = function(msg) {
  var html = `<strong>${typeof msg['title'] !== 'undefined' ? msg['title'] : ''}</strong>${msg['message']}`;

  return html;
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

/** Add the current profile to the interested profiles list. */
var add_interest = function(bounty_pk, data) {
  if (document.interested) {
    return;
  }
  mutate_interest(bounty_pk, 'new', data);
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
  $.post(request_url, data).then(function(result) {
    hideBusyOverlay();

    result = sanitizeAPIResults(result);

    if (result.success) {
      if (direction === 'new') {
        _alert({ message: result.msg }, 'success');
        $('#interest a').attr('id', 'btn-white');
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

var retrieveIssueDetails = function() {
  var ele = $('input[name=issueURL]');
  var target_eles = {
    'title': $('input[name=title]'),
    'keywords': $('input[name=keywords]'),
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
  $.get(request_url, function(result) {
    result = sanitizeAPIResults(result);
    if (result['keywords']) {
      var keywords = result['keywords'];

      target_eles['keywords'].val(keywords.join(', '));
    }
    target_eles['description'].val(result['description']);
    target_eles['title'].val(result['title']);

    $('#title--text').html(result['title']); // TODO: Refactor
    $.each(target_eles, function(i, ele) {
      ele.removeClass('loading');
    });
  }).fail(function() {
    $.each(target_eles, function(i, ele) {
      ele.removeClass('loading');
    });
  });
};


var randomElement = function(array) {
  var length = array.length;
  var randomNumber = Math.random();
  var randomIndex = Math.floor(randomNumber * length);

  return array[randomIndex];
};

var mixpanel_track_once = function(event, params) {
  if (document.listen_for_web3_iterations == 1 && mixpanel) {
    mixpanel.track(event, params);
  }
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
        info = gettext('Web3 locked. Please unlock ') +
          '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>';
        $('#current-network').text(gettext('Metamask Locked'));
        $('#navbar-network-banner').html(info);
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
        info = gettext('Web3 locked. Please unlock ') +
          '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>';
        $('#current-network').text(gettext('Metamask Locked'));
        $('#navbar-network-banner').html(info);
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

var trigger_primary_form_web3_hooks = function() {
  // detect web3, and if not, display a form telling users they must be web3 enabled.
  var params = {
    page: document.location.pathname
  };

  if ($('#primary_form').length) {
    var is_zero_balance_not_okay = document.location.href.indexOf('/faucet') == -1;

    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
      mixpanel_track_once('No Metamask Error', params);
    } else if (!web3.eth.coinbase) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');
      mixpanel_track_once('Unlock Metamask Error', params);
    } else if (is_zero_balance_not_okay && document.balance == 0) {
      $('#zero_balance_error').css('display', 'block');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
      mixpanel_track_once('Zero Balance Metamask Error', params);
    } else {
      $('#zero_balance_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'block');
      $('#robot_error').addClass('hidden');
      $('#primary_form').removeClass('hidden');
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
      mixpanel_track_once('No Metamask Error', params);
      return;
    } else if (!web3.eth.coinbase) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    } else if (balance >= faucet_amount) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#over_balance_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      mixpanel_track_once('Faucet Available Funds Metamask Error', params);
    } else {
      $('#over_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#faucet_form').removeClass('hidden');
    }
  }
  if ($('#admin_faucet_form').length) {
    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      mixpanel_track_once('No Metamask Error', params);
      return;
    }
    if (!web3.eth.coinbase) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      mixpanel_track_once('Unlock Metamask Error', params);
      return;
    }
    web3.eth.getBalance(web3.eth.coinbase, function(errors, result) {
      var balance = result.toNumber();

      if (balance == 0) {
        $('#zero_balance_error').css('display', 'block');
        $('#admin_faucet_form').remove();
        mixpanel_track_once('Zero Balance Metamask Error', params);
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
var listen_for_web3_changes = function() {

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
    web3.eth.getBalance(web3.eth.coinbase, function(errors, result) {
      if (typeof result != 'undefined') {
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
  setInterval(listen_for_web3_changes, 300);
  attach_close_button();
});

var promptForAuth = function(event) {
  var denomination = $('#token option:selected').text();
  var tokenAddress = $('#token option:selected').val();

  if (!denomination) {
    return;
  }

  if (denomination == 'ETH') {
    $('input, textarea, select').prop('disabled', '');
  } else {
    var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
    var from = web3.eth.coinbase;
    var to = bounty_address();

    token_contract.allowance.call(from, to, function(error, result) {
      if (error || result.toNumber() == 0) {
        if (!document.alert_enable_token_shown) {
          _alert(
            gettext('To enable this token, go to the ') +
            '<a style="padding-left:5px;" href="/settings/tokens">' +
            gettext('Token Settings page and enable it.') +
            '</a> ' +
            gettext('This is only needed once per token.'),
            'warning'
          );
        }
        document.alert_enable_token_shown = true;

        $('input, textarea, select').prop('disabled', 'disabled');
        $('select[name=denomination]').prop('disabled', '');
      } else {
        $('input, textarea, select').prop('disabled', '');
      }
    });

  }
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

    result['rounded_amount'] = normalizeAmount(result['value_in_token'] / divisor, decimals);

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
    const projectType = ucwords(result['project_type']) + ' &bull; ';

    result['action'] = result['url'];
    result['title'] = result['title'] ? result['title'] : result['github_url'];
    result['p'] = projectType + (result['experience_level'] ? (result['experience_level'] + ' &bull; ') : '');

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

      result['p'] += ('Expired ' + timeAgo + ' ago');
    } else {
      const openedWhen = timeDifference(dateNow, new Date(result['web3_created']), true);
      const timeLeft = timeDifference(dateNow, dateExpires);
      const expiredExpires = dateNow < dateExpires ? 'Expires' : 'Expired';

      result['p'] += ('Opened ' + openedWhen + ' ago, ' + expiredExpires + ' ' + timeLeft);
    }

    if (renderForExplorer) {
      if (typeof web3 != 'undefined' && web3.eth.coinbase == result['bounty_owner_address']) {
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
  return Math.round(amount * 10 ** decimals) / 10 ** decimals;
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
