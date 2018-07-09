/* eslint-disable no-console */

$(document).ready(function() {

  // jquery bindings
  $("#advanced_toggle").click(function(){
    advancedToggle();
  });
  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
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
  var tokenAddress = $('#token').val();
  var gas_money = Math.pow(10, (9 + 5)) * ((defaultGasPrice * 1.001) / Math.pow(10, 9));
  var expires = parseInt($('#expires').val());
  var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
  var tokenDetails = tokenAddressToDetails(tokenAddress);
  var tokenName = 'ETH';
  var weiConvert = Math.pow(10, 18);

  if (!isSendingETH) {
    tokenName = tokenDetails.name;
    weiConvert = Math.pow(10, tokenDetails.decimals);
  }
  var amountInEth = parseFloat($('#amount').val());
  var amountInWei = amountInEth * 1.0 * weiConvert;
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
  if (!isNumeric(amountInWei) || amountInWei == 0) {
    _alert({ message: gettext('You must enter an number for the amount!') }, 'warning');
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

  const url = '/tip/send/3';
  fetch(url, {
    method: 'POST',
    body: JSON.stringify({
      username: username,
      email: email,
      tokenName: tokenName,
      amount: amountInWei,
      comments_priv: comments_priv,
      comments_public: comments_public,
      expires_date: expires,
      github_url: github_url,
      from_email: from_email,
      from_name: from_name,
      tokenAddress: tokenAddress,
      network: document.web3network,
      from_address: fromAccount
    })
  }).then(function(response) {
    return response.json();
  }).then(function(json) {
    var is_success = json['status'] == 'OK';
    var _class = is_success ? 'info' : 'error';
    if(!is_success){
      _alert(json, _class);
    } else {
      var destinationAccount = json.payload.address;
      var post_send_callback = function(errors, txid){
        if(errors){
          _alert({ message: gettext('There was an error.') }, 'warning');
        } else {
          const url = '/tip/send/4';
          fetch(url, {
            method: 'POST',
            body: JSON.stringify({
              destinationAccount: destinationAccount,
              txid: txid,
            })
          }).then(function(response) {
            return response.json();
          }).then(function(json) {
            var is_success = json['status'] == 'OK';
            if(!is_success){
              _alert(json, _class);
            } else {
              $('#loading_trans').html('This transaction has been sent 👌');
              $('#send_eth').css('display', 'none');
              $('#send_eth_done').css('display', 'block');
              $('#tokenName').html(tokenName);
              $('#new_username').html(username);
              $('#trans_link').attr('href','https://' + etherscanDomain() + '/tx/' + txid);
              $('#trans_link2').attr('href','https://' + etherscanDomain() + '/tx/'+ txid);
            }
          });
        }
      };
      if(isSendingETH){
        web3.eth.sendTransaction({
          to: destinationAccount,
          value: amountInWei,
        }, post_send_callback);
      } else {
        var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
        token_contract(tokenAddress).transfer(destinationAccount, amountInWei, {value: gas_money}, post_send_callback);
      }
    }
  });


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

var etherscanDomain = function() {
  var etherscanDomain = 'etherscan.io';

  if (document.web3network == 'custom network') {
    // testrpc
    etherscanDomain = 'localhost';
  } else if (document.web3network == 'rinkeby') {
    // rinkeby
    etherscanDomain = 'rinkeby.etherscan.io';
  } else {
    // mainnet
  }
  return etherscanDomain;
};
