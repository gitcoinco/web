/* eslint-disable no-console */

$(document).ready(function() {

  // jquery bindings
  $("#advanced_toggle").click(function(){
    advancedToggle();
  });
  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
  $('#token').on('change', promptForAuth);
  $("#send").click(function(e){
    return send(e);
  });

});

function advancedToggle() {
  $('#advanced_toggle').css('display', 'none')
  $('#advanced').css('display', 'block')
  return false;
}

function validateEmail(email) {
  var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

  return re.test(email);
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}



function send(e) {

  mixpanel.track('Tip Step 2 Click', {});
  e.preventDefault();
  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
    return;
  }
  // setup
  var fromAccount = web3.eth.accounts[0];

  // get form data
  var email = $('#email').val();
  var github_url = $('#issueURL').val();
  var from_name = $('#fromName').val();
  var username = $('#username').val();

  if (username.indexOf('@') == -1) {
    username = '@' + username;
  }
  var _disableDeveloperTip = true;
  var accept_tos = $('#tos').is(':checked');
  var token = $('#token').val();
  var fees = 0;
  var expires = parseInt($('#expires').val());
  var isSendingETH = (token == '0x0' || token == '0x0000000000000000000000000000000000000000');
  var tokenDetails = tokenAddressToDetails(token);
  var tokenName = 'ETH';
  var weiConvert = 10 ** 9;

  if (!isSendingETH) {
    tokenName = tokenDetails.name;
    weiConvert = Math.pow(10, tokenDetails.decimals);
  }
  var amount = $('#amount').val() * weiConvert;
  var amountInEth = amount * 1.0 / weiConvert;
  var comments_priv = $('#comments_priv').val();
  var comments_public = $('#comments_public').val();
  var from_email = $('#fromEmail').val();
  // validation
  var hasEmail = email != '';
  var hasUsername = username != '';

  // validation
  if (hasEmail && !validateEmail(email)) {
    _alert({ message: gettext('To Email is optional, but if you enter an email, you must enter a valid email!') }, 'warning');
    return;
  }
  if (from_email != '' && !validateEmail(from_email)) {
    _alert({ message: gettext('From Email is optional, but if you enter an email, you must enter a valid email!') }, 'warning');
    return;
  }
  if (!isNumeric(amount) || amount == 0) {
    _alert({ message: gettext('You must enter an number for the amount!') }, 'warning');
    return;
  }

  var min_send_amt_wei = 0;
  var min_amount = min_send_amt_wei * 1.0 / weiConvert;
  var max_amount = 5;

  if (!isSendingETH) {
    max_amount = 1000;
  }
  if (amountInEth > max_amount) {
    _alert({ message: gettext('You can only send a maximum of ' + max_amount + ' ' + tokenName + '.') }, 'warning');
    return;
  }
  if (amountInEth < min_amount) {
    _alert({ message: gettext('You can only send a minimum of ' + min_amount + ' ' + tokenName + '.') }, 'warning');
    return;
  }
  if (username == '') {
    _alert({ message: gettext('You must enter a username.') }, 'warning');
    return;
  }
  if (!accept_tos) {
    _alert({ message: gettext('You must accept the terms.') }, 'warning');
    return;
  }


  alert("todo");
}

var updateEstimate = function(e) {
  var denomination = $('#token option:selected').text();
  var amount = $('#amount').val();

  getUSDEstimate(amount, denomination, function(usdAmount) {
    if (usdAmount && usdAmount['full_text']) {
      $('#usd_amount').html(usdAmount['full_text']);
    } else {
      $('#usd_amount').html('</br>');
    }
  })
};

// TODO: DRY
var promptForAuth = function(event) {
  var denomination = $('#token option:selected').text();
  var tokenAddress = $('#token option:selected').val();

  if (denomination == 'ETH') {
    $('input, textarea, select').prop('disabled', '');
  } else {
    var from = web3.eth.coinbase;
    var to = contract().address;
    alert('todo');
  }
};
