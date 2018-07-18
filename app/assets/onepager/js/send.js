/* eslint-disable no-console */

var get_smtp_token = function(){
  var local_token = "71b3882d-37fd-4c1c-b510-80e223baa283";
  var prod_token = "7c625911-27e1-45eb-8e32-7cae47a87840"
  var stage_token = "b9a30d31-c0d2-4088-8f3e-e97c0bbde3c8";

  var token = local_token;
  if(document.location.hostname=='gitcoin.co') token=prod_token;
  if(document.location.hostname=='stage.gitcoin.co') token=stage_token;
  return token;
}

var get_metadata = function(callback){
  // test of using shamirs secret to break apart a pk
  var account = new Accounts().new();
  var address = account['address'];
  var public = account['public'];
  var private = account['private'];
  var shares = secrets.share(private, 3, 2);

  ipfs = get_ipfs();
  ipfs.add(shares[1], function(err, hash1) {
    if (err) throw err;
    ipfs.add(shares[2], function(err, hash2) {
      if (err) throw err;
      callback({
          'pub_key': public,
          'address': address,
          'reference_hash_for_funder': hash1,
          'reference_hash_for_receipient': hash2,
          'gitcoin_secret': shares[0],
      });
    });
  });

}

var send_email = function(){
  Email.send("kevin@gitcoin.co",
  "kevin@gitcoin.co",
  "This is a subject",
  "this is the body",
  {token: get_smtp_token()});
}

$(document).ready(function() {

  // jquery bindings
  $('#advanced_toggle').click(function() {
    advancedToggle();
  });
  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
  $('#send').click(function(e) {
    e.preventDefault();
    if($(this).hasClass('disabled')) return;
    loading_button($(this));

    // get form data
    var email = $('#email').val();
    var github_url = $('#issueURL').val();
    var from_name = $('#fromName').val();
    var username = $('#username').val();
    var amountInEth = parseFloat($('#amount').val());
    var comments_priv = $('#comments_priv').val();
    var comments_public = $('#comments_public').val();
    var from_email = $('#fromEmail').val();
    var accept_tos = $('#tos').is(':checked');
    var tokenAddress = $('#token').val();
    var expires = parseInt($('#expires').val());

    // derived info
    var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
    var tokenDetails = tokenAddressToDetails(tokenAddress);
    var tokenName = 'ETH';
    var weiConvert = Math.pow(10, 18);

    if (!isSendingETH) {
      tokenName = tokenDetails.name;
    }

    var success_callback = function(txid) {

      startConfetti();
      var url = 'https://' + etherscanDomain() + '/tx/' + txid;

      $('#loading_trans').html('This transaction has been sent 👌');
      $('#send_eth').css('display', 'none');
      $('#send_eth_done').css('display', 'block');
      $('#tokenName').html(tokenName);
      $('#new_username').html(username);
      $('#trans_link').attr('href', url);
      $('#trans_link2').attr('href', url);
      unloading_button($(this));
    };
    var failure_callback = function(){
      unloading_button($("#send"));
    };

    return sendTip(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, false);

  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      if (ele && ele.addr) {
        var html = '<option value=' + ele.addr + '>' + ele.name + '</option>';

        $('#token').append(html);
      }
    });
    jQuery('#token').select2();
  });

});

function advancedToggle() {
  $('#advanced_toggle').css('display', 'none');
  $('#advanced').css('display', 'block');
  return false;
}

function validateEmail(email) {
  var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

  return re.test(email);
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}


function sendTip(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, is_for_bounty_fulfiller) {

  mixpanel.track('Tip Step 2 Click', {});
  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
    failure_callback();
    return;
  }
  // setup
  var fromAccount = web3.eth.accounts[0];

  if (username.indexOf('@') == -1) {
    username = '@' + username;
  }
  var _disableDeveloperTip = true;
  var gas_money = parseInt(Math.pow(10, (9 + 5)) * ((defaultGasPrice * 1.001) / Math.pow(10, 9)));
  var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
  var tokenDetails = tokenAddressToDetails(tokenAddress);
  var tokenName = 'ETH';
  var weiConvert = Math.pow(10, 18);

  if (!isSendingETH) {
    tokenName = tokenDetails.name;
    weiConvert = Math.pow(10, tokenDetails.decimals);
  }
  var amountInWei = amountInEth * 1.0 * weiConvert;
  // validation
  var hasEmail = email != '';
  var hasUsername = username != '';

  // validation
  if (hasEmail && !validateEmail(email)) {
    _alert({ message: gettext('To Email is optional, but if you enter an email, you must enter a valid email!') }, 'warning');
    failure_callback();
    return;
  }
  if (from_email != '' && !validateEmail(from_email)) {
    _alert({ message: gettext('From Email is optional, but if you enter an email, you must enter a valid email!') }, 'warning');
    failure_callback();
    return;
  }
  if (!isNumeric(amountInWei) || amountInWei == 0) {
    _alert({ message: gettext('You must enter an number for the amount!') }, 'warning');
    failure_callback();
    return;
  }
  if (username == '') {
    _alert({ message: gettext('You must enter a username.') }, 'warning');
    failure_callback();
    return;
  }
  if (!accept_tos) {
    _alert({ message: gettext('You must accept the terms.') }, 'warning');
    failure_callback();
    return;
  }

  get_metadata(function(metadata){
    const url = '/tip/send/3';

    fetch(url, {
      method: 'POST',
      body: JSON.stringify({
        username: username,
        email: email,
        tokenName: tokenName,
        amount: amountInEth,
        comments_priv: comments_priv,
        comments_public: comments_public,
        expires_date: expires,
        github_url: github_url,
        from_email: from_email,
        from_name: from_name,
        tokenAddress: tokenAddress,
        network: document.web3network,
        from_address: fromAccount,
        is_for_bounty_fulfiller: is_for_bounty_fulfiller,
        metadata: metadata,
      })
    }).then(function(response) {
      return response.json();
    }).then(function(json) {
      var is_success = json['status'] == 'OK';
      var _class = is_success ? 'info' : 'error';

      if (!is_success) {
        _alert(json, _class);
      } else {
        var destinationAccount = metadata['address'];
        var post_send_callback = function(errors, txid) {
          if (errors) {
            _alert({ message: gettext('There was an error.') }, 'warning');
          } else {
            const url = '/tip/send/4';

            fetch(url, {
              method: 'POST',
              body: JSON.stringify({
                destinationAccount: destinationAccount,
                txid: txid
              })
            }).then(function(response) {
              return response.json();
            }).then(function(json) {
              var is_success = json['status'] == 'OK';

              if (!is_success) {
                _alert(json, _class);
              } else {
                success_callback(txid);
              }
            });
          }
        };

        if (isSendingETH) {
          web3.eth.sendTransaction({
            to: destinationAccount,
            value: amountInWei
          }, post_send_callback);
        } else {
          _alert({ message: gettext('You will now be asked to confirm two transactions.  The first is gas money, so your receipient doesnt have to pay it.  The second is the actual token transfer.') }, 'info');
          web3.eth.sendTransaction({
            to: destinationAccount,
            value: gas_money
          }, function() {
            var token_contract = web3.eth.contract(token_abi).at(tokenAddress);

            token_contract.transfer(destinationAccount, amountInWei, post_send_callback);
          });
        }
      }
    });
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
  });
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
