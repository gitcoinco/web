/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
// helper functions

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
  button.prepend('<img src=/static/v2/images/loading_white.gif style="max-width:20px; max-height: 20px">').addClass('disabled');
};


var update_metamask_conf_time_and_cost_estimate = function() {
  var confTime = 'unknown';
  var ethAmount = 'unknown';
  var usdAmount = 'unknown';

  var gasLimit = parseInt($('#gasLimit').val());
  var gasPrice = parseFloat($('#gasPrice').val());

  if (gasPrice) {
    ethAmount = Math.round(1000 * gasLimit * gasPrice / Math.pow(10, 9)) / 1000;
    usdAmount = Math.round(10 * ethAmount * document.eth_usd_conv_rate) / 10;
  }

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

var unloading_button = function(button) {
  button.prop('disabled', false);
  button.removeClass('disabled');
  button.find('img').remove();
};

var sanitizeDict = function(d) {
  if (typeof d != 'object') {
    return d;
  }
  keys = Object.keys(d);
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];

    d[key] = sanitize(d[key]);
  }
  return d;
};

var sanitizeAPIResults = function(results) {
  for (var i = 0; i < results.length; i++) {
    results[i] = sanitizeDict(results[i]);
  }
  return results;
};

var sanitize = function(str) {
  if (typeof str != 'string') {
    return str;
  }
  result = str.replace(/>/g, '&gt;').replace(/</g, '&lt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  return result;
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
      `<div class="alert ${_class}" style="top: ${top}px">
        <div class="message">
          ${alertMessage(msg)}
        </div>
        ${closeButton(msg)}
      </div>;`
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
var remove_interest = function(bounty_pk) {
  if (!document.interested) {
    return;
  }
  mutate_interest(bounty_pk, 'remove');
};

/** Helper function -- mutates interests in either direction. */
var mutate_interest = function(bounty_pk, direction, data) {
  var request_url = '/actions/bounty/' + bounty_pk + '/interest/' + direction + '/';

  $('#submit').toggleClass('none');
  $('#interest a').toggleClass('btn')
    .toggleClass('btn-small')
    .toggleClass('button')
    .toggleClass('button--primary');

  if (direction === 'new') {
    _alert({message: "Thanks for letting us know that you're ready to start work."}, 'success');
    $('#interest a').attr('id', 'btn-white');
  } else if (direction === 'remove') {
    _alert({message: "You've stopped working on this, thanks for letting us know."}, 'success');
    $('#interest a').attr('id', '');
  }

  $.post(request_url, data).then(function(result) {
    result = sanitizeAPIResults(result);
    if (result.success) {
      pull_interest_list(bounty_pk);
      return true;
    }
    return false;
  }).fail(function(result) {
    alert(result.responseJSON.error);
  });
};


var uninterested = function(bounty_pk, profileId) {
  var request_url = '/actions/bounty/' + bounty_pk + '/interest/' + profileId + '/uninterested/';

  $.post(request_url, function(result) {
    result = sanitizeAPIResults(result);
    if (result.success) {
      _alert({message: 'Contributor removed from bounty.'}, 'success');
      pull_interest_list(bounty_pk);
      return true;
    }
    return false;
  }).fail(function(result) {
    _alert({message: 'got an error. please try again, or contact support@gitcoin.co'}, 'error');
  });
};


/** Pulls the list of interested profiles from the server. */
var pull_interest_list = function(bounty_pk, callback) {
  document.interested = false;
  var uri = '/actions/api/v0.1/bounties/?github_url=' + document.issueURL;
  var started = [];

  $.get(uri, function(results) {
    render_activity(results[0]);
    if (results[0].interested) {
      var interested = results[0].interested;

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


var sidebar_redirect_triggers = function() {
  $('.sidebar_search input[type=radio], .sidebar_search label').change(function(e) {
    if (document.location.href.indexOf('/dashboard') == -1 && document.location.href.indexOf('/explorer') == -1) {
      document.location.href = '/explorer';
      e.preventDefault();
    }
  });
};

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

var attach_close_button = function() {
  $('body').delegate('.alert .closebtn', 'click', function(e) {
    $(this).parents('.alert').remove();
    $('.alert').each(function() {
      var old_top = $(this).css('top');
      var new_top = (parseInt(old_top.replace('px')) - 66) + 'px';

      $(this).css('top', new_top);
    });
  });
};


// callbacks that can retrieve various metadata about a github issue URL

var retrieveAmount = function() {
  var ele = $('input[name=amount]');
  var target_ele = $('#usd_amount');

  if (target_ele.html() == '') {
    target_ele.html('<img style="width: 50px; height: 50px;" src=/static/v2/images/loading_v2.gif>');
  }

  var amount = $('input[name=amount]').val();
  var address = $('select[name=deonomination]').val();
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
  var request_url = '/sync/get_issue_details?url=' + encodeURIComponent(issue_url);

  $.each(target_eles, function(i, ele) {
    ele.addClass('loading');
  });
  $.get(request_url, function(result) {
    result = sanitizeAPIResults(result);
    if (result['keywords']) {
      var keywords = result['keywords'];

      target_eles['keywords'].val(keywords.join(', '));
    }
    if (result['description']) {
      target_eles['description'].val(result['description']);
    }
    if (result['title']) {
      target_eles['title'].val(result['title']);
    }
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

var trigger_sidebar_web3_disabled = function() {
  $('#upper_left').addClass('disabled');
  $('#sidebar_head').html('<i class="fa fa-question"></i>');
  $('#sidebar_p').html('<p>Web3 disabled</p><p>Please install <a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a> <br> <a href="/web3" target="_blank" rel="noopener noreferrer">What is Metamask and why do I need it?</a>.</p>');
};

var trigger_sidebar_web3_locked = function() {
  $('#upper_left').addClass('disabled');
  $('#sidebar_head').html('<i class="fa fa-lock"></i>');
  $('#sidebar_p').html('<p>Web3 locked</p><p>Please unlock <a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">Metamask</a>.<p>');
};

var mixpanel_track_once = function(event, params) {
  if (document.listen_for_web3_iterations == 1 && mixpanel) {
    mixpanel.track(event, params);
  }
};

var trigger_sidebar_web3 = function(network) {
  document.web3network = network;

  // is this a supported networK?
  var is_supported_network = true;

  var recommended_network = 'mainnet or rinkeby';

  if (network == 'kovan' || network == 'ropsten') {
    is_supported_network = false;
  }
  if (document.location.href.indexOf('https://gitcoin.co') != -1) {
    if (network != 'mainnet' && network != 'rinkeby') {
      is_supported_network = false;
      recommended_network = 'mainnet or rinkeby';
    }
  }
  if (network == 'mainnet') {
    if (document.location.href.indexOf('https://gitcoin.co') == -1) {
      is_supported_network = false;
      recommended_network = 'custom rpc via ganache-cli / rinkeby';
    }
  }
  var sidebar_p = '<p>Connected to ' + network + '.</p>';

  if (is_supported_network) {
    $('#upper_left').removeClass('disabled');
    $('#sidebar_head').html("<i class='fa fa-wifi'></i>");
    $('#sidebar_p').html('<p>Web3 enabled<p>' + sidebar_p);
  } else {
    $('#upper_left').addClass('disabled');
    $('#sidebar_head').html("<i class='fa fa-battery-empty'></i>");
    sidebar_p += '<p>(try ' + recommended_network + ')</p>';
    $('#sidebar_p').html('<p>Unsupported network</p>' + sidebar_p);
  }
};


var trigger_primary_form_web3_hooks = function() {
  // detect web3, and if not, display a form telling users they must be web3 enabled.
  var params = {
    page: document.location.pathname
  };

  if ($('#primary_form').length) {
    var is_zero_balance_not_okay = document.location.href.indexOf('/faucet') == -1;

    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#primary_form').addClass('hidden');
      mixpanel_track_once('No Metamask Error', params);
    } else if (!web3.eth.coinbase) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#primary_form').addClass('hidden');
      mixpanel_track_once('Unlock Metamask Error', params);
    } else if (is_zero_balance_not_okay && document.balance == 0) {
      $('#zero_balance_error').css('display', 'block');
      $('#primary_form').addClass('hidden');
      mixpanel_track_once('Zero Balance Metamask Error', params);
    } else {
      $('#zero_balance_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#primary_form').removeClass('hidden');
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

// figure out what version of web3 this is, whether we're logged in, etc..
var listen_for_web3_changes = function() {

  if (!document.listen_for_web3_iterations) {
    document.listen_for_web3_iterations = 1;
  } else {
    document.listen_for_web3_iterations += 1;
  }

  if (typeof web3 == 'undefined') {
    trigger_sidebar_web3_disabled();
    trigger_form_hooks();
  } else if (typeof web3 == 'undefined' || typeof web3.eth == 'undefined' || typeof web3.eth.coinbase == 'undefined' || !web3.eth.coinbase) {
    trigger_sidebar_web3_locked();
    trigger_form_hooks();
  } else {
    web3.eth.getBalance(web3.eth.coinbase, function(errors, result) {
      if (typeof result != 'undefined') {
        document.balance = result.toNumber();
      }
    });

    web3.version.getNetwork((error, netId) => {
      if (error) {
        trigger_sidebar_web3_disabled();
      } else {
        // figure out which network we're on
        var network = 'unknown';

        switch (netId) {
          case '1':
            network = 'mainnet';
            break;
          case '2':
            network = 'morden';
            break;
          case '3':
            network = 'ropsten';
            break;
          case '4':
            network = 'rinkeby';
            break;
          case '42':
            network = 'kovan';
            break;
          default:
            network = 'custom network';
        }
        trigger_sidebar_web3(network);
        trigger_form_hooks();
      }
    });
  }
};

var actions_page_warn_if_not_on_same_network = function() {
  var user_network = document.web3network;

  if (typeof user_network == 'undefined') {
    user_network = 'no network';
  }
  var bounty_network = $('input[name=network]').val();

  if (bounty_network != user_network) {
    var msg = 'Warning: You are on ' + user_network + ' and this bounty is on the ' + bounty_network + ' network.  Please change your network to the ' + bounty_network + ' network.';

    _alert({message: gettext(msg)}, 'error');
  }
};

$(document).ready(function() {
  sidebar_redirect_triggers();
  attach_change_element_type();
  attach_close_button();
});

window.addEventListener('load', function() {
  setInterval(listen_for_web3_changes, 300);
});

var setUsdAmount = function(event) {
  var amount = $('input[name=amount]').val();
  var denomination = $('#token option:selected').text();
  var estimate = getUSDEstimate(amount, denomination, function(estimate) {
    $('#usd_amount').html(estimate);
  });
};
