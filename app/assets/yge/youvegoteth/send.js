/* eslint-disable no-console */
function validateEmail(email) {
  var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

  return re.test(email);
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function advancedToggle() {
  $('advanced_toggle').style.display = 'none';
  $('advanced').style.display = 'block';
  return false;
}

var unPackAddresses = function() {
  var addresses = JSON.parse(localStorage.getItem('addresses'));

  document.addresses = addresses;
  if (!addresses || addresses.length == 0) {
    _alert({message: 'Invalid addresses generated. Please try again from the first page.'}, 'warning');
    setTimeout(function() {
      if (document.location.href.indexOf('send') != -1) {
        document.location.href = '/tip/send';
      }
    }, 3000);
  }
  localStorage.setItem('addresses', null);
};
var updateEstimate = function(e) {
  var denomination = jQuery('#token option:selected').text();
  var amount = jQuery('#amount').val();

  getUSDEstimate(amount, denomination, function(usdAmount) {
    if (usdAmount) {
      jQuery('#usd_amount').html(usdAmount);
    } else {
      jQuery('#usd_amount').html('</br>');
    }
  });

};

window.onload = function() {
  jQuery('#amount').on('keyup blur change', updateEstimate);
  jQuery('#token').on('change', updateEstimate);

  unPackAddresses();

  var min_send_amt_wei = 6000000;

  if (localStorage['amount']) {
    $('amount').value = localStorage['amount'];
  }
  if (localStorage['username']) {
    $('username').value = localStorage['username'];
  }
  if (localStorage['issueURL']) {
    $('issueURL').value = localStorage['issueURL'];
  }
  if (localStorage['email']) {
    $('email').value = localStorage['email'];
  }
  if (localStorage['fromName']) {
    $('fromName').value = localStorage['fromName'];
  }
  if (localStorage['fromEmail']) {
    $('fromEmail').value = localStorage['fromEmail'];
  }
  if (localStorage['comments_priv']) {
    $('comments_priv').value = localStorage['comments_priv'];
  }
  if (localStorage['comments_public']) {
    $('comments_public').value = localStorage['comments_public'];
  }
  if (localStorage['expires']) {
    $('expires').selectedIndex = localStorage['expires'];
  }

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      var option = document.createElement('option');

      option.text = ele.name;
      option.value = ele.addr;
      $('token').add(option);
    });
    jQuery('#token').select2();
  });

  // When 'Generate Account' is clicked
  $('send').onclick = function(e) {
    mixpanel.track('Tip Step 2 Click', {});
    e.preventDefault();
    if (metaMaskWarning()) {
      return;
    }
    // setup
    var fromAccount = web3.eth.accounts[0];

    // get form data
    var email = $('email').value;
    var github_url = $('issueURL').value;
    var from_name = $('fromName').value;
    var username = $('username').value;

    if (username.indexOf('@') == -1) {
      username = '@' + username;
    }
    var _disableDeveloperTip = true;
    var accept_tos = $('tos').checked;
    var token = $('token').value;
    var fees = Math.pow(10, (9 + 5)) * ((defaultGasPrice * 1.001) / Math.pow(10, 9));
    var expires = parseInt($('expires').value);
    var isSendingETH = (token == '0x0' || token == '0x0000000000000000000000000000000000000000');
    var tokenDetails = tokenAddressToDetails(token);
    var tokenName = 'ETH';
    var weiConvert = weiPerEther;

    if (!isSendingETH) {
      tokenName = tokenDetails.name;
      weiConvert = Math.pow(10, tokenDetails.decimals);
    }
    var amount = $('amount').value * weiConvert;
    var amountInEth = amount * 1.0 / weiConvert;
    var comments_priv = $('comments_priv').value;
    var comments_public = $('comments_public').value;
    var from_email = $('fromEmail').value;
    // validation
    var hasEmail = email != '';
    var hasUsername = username != '';

    // validation
    if (hasEmail && !validateEmail(email)) {
      _alert({message: 'To Email is optional, but if you enter an email, you must enter a valid email!'}, 'warning');
      return;
    }
    if (from_email != '' && !validateEmail(from_email)) {
      _alert({message: 'From Email is optional, but if you enter an email, you must enter a valid email!'}, 'warning');
      return;
    }
    if (!isNumeric(amount) || amount == 0) {
      _alert({message: 'You must enter an number for the amount!'}, 'warning');
      return;
    }
    var min_amount = min_send_amt_wei * 1.0 / weiConvert;
    var max_amount = 5;

    if (!isSendingETH) {
      max_amount = 1000;
    }
    if (amountInEth > max_amount) {
      _alert({message: 'You can only send a maximum of ' + max_amount + ' ' + tokenName + '.'}, 'warning');
      return;
    }
    if (amountInEth < min_amount) {
      _alert({message: 'You can only send a minimum of ' + min_amount + ' ' + tokenName + '.'}, 'warning');
      return;
    }
    if (username == '') {
      _alert({message: 'You must enter a username.'}, 'warning');
      return;
    }
    if (!accept_tos) {
      _alert({message: 'You must accept the terms.'}, 'warning');
      return;
    }

    localStorage['amount'] = amountInEth;
    localStorage['username'] = username;
    localStorage['issueURL'] = github_url;
    localStorage['fromName'] = from_name;
    localStorage['fromEmail'] = from_email;
    localStorage['email'] = email;
    localStorage['comments_priv'] = comments_priv;
    localStorage['comments_public'] = comments_public;
    localStorage['expires'] = $('expires').selectedIndex;

    loading_button(jQuery('#send'));
    var numBatches = document.addresses.length;
    var plural = numBatches > 1 ? 's' : '';
    var processTx = function(i) {
      // generate ephemeral account
      var _owner = '0x' + lightwallet.keystore._computeAddressFromPrivKey(document.addresses[i].pk);
      var _private_key = document.addresses[i]['pk'];

      // set up callback for web3 call to final transfer
      var final_callback = function(error, result) {
        if (error) {
          console.log(error);
          mixpanel.track('Tip Step 2 Error', {step: 'final', error: error});
          _alert({message: 'got an error :('}, 'error');
          unloading_button(jQuery('#send'));
        } else {
          dataLayer.push({'event': 'sendtip'});
          mixpanel.track('Tip Step 2 Success', {});
          var txid = result;

          $('send_eth').style.display = 'none';
          $('tokenName').innerHTML = tokenName;
          $('send_eth_done').style.display = 'block';
          $('trans_link').href = 'https://' + etherscanDomain() + '/tx/' + result;
          $('trans_link2').href = 'https://' + etherscanDomain() + '/tx/' + result;
          var relative_link = '?n=' + document.web3network + '&txid=' + txid + '&key=' + _private_key + '&gasPrice=' + (defaultGasPrice / Math.pow(10, 9));
          var base_url = document.location.href.split('?')[0].replace('send/2', 'receive').replace('#', '');
          var link = base_url + relative_link;

          $('new_username').innerHTML = username;
          var warning = getWarning();

          callFunctionWhenTransactionMined(txid, function() {
            $('loading_trans').innerHTML = 'This transaction has been confirmed 👌';
          });
          const url = '/tip/send/2';

          fetch(url, {
            method: 'POST',
            body: JSON.stringify({
              url: link,
              username: username,
              email: email,
              tokenName: tokenName,
              amount: amount / weiConvert,
              comments_priv: comments_priv,
              comments_public: comments_public,
              expires_date: expires,
              github_url: github_url,
              from_email: from_email,
              from_name: from_name,
              tokenAddress: token,
              network: document.web3network,
              from_address: fromAccount,
              txid: txid
            })
          }).then(function(response) {
            return response.json();
          }).then(function(json) {
            var is_success = json['status'] == 'OK';
            var _class = is_success ? 'info' : 'error';
            
            _alert(json, _class);
          });

          if ((i + 1) < numBatches) {
            processTx(i + 1);
          }
        }
      };

      // set up callback for web3 call to erc20 callback
      var erc20_callback = function(error, result) {
        if (error) {
          console.error(error);
          _alert({message: 'got an error :('}, 'error');
          unloading_button(jQuery('#send'));
        } else {
          var approve_amount = amount * numBatches;

          token_contract(token).approve.estimateGas(contract_address(), approve_amount, function(error, result) {
            var _gas = result;

            if (_gas > maxGas) {
              _gas = maxGas;
            }
            var _gasLimit = parseInt(_gas * 1.01);

            token_contract(token).approve.sendTransaction(
              contract_address(),
              approve_amount,
              {from: fromAccount, gas: web3.toHex(gas), gasLimit: web3.toHex(gasLimit)},
              final_callback);
          });
        }
      };


      // send transfer to web3
      var next_callback = null;
      var amountETHToSend = null;

      if (isSendingETH) {
        next_callback = final_callback;
        amountETHToSend = parseInt(amount + fees);
      } else {
        amountETHToSend = parseInt(min_send_amt_wei + fees);
        if (i == 0) { // only need to call approve once for amount * numbatches
          next_callback = erc20_callback;
        } else {
          next_callback = final_callback;
        }
      }
      var _gas = recommendGas;

      if (_gas > maxGas) {
        _gas = maxGas;
      }
      if (_gas > recommendGas) {
        _gas = recommendGas;
      }
      var _gasLimit = parseInt(_gas * 1.01);

      contract().newTransfer.sendTransaction(
        _disableDeveloperTip,
        _owner,
        token,
        amount,
        fees,
        expires,
        {from: fromAccount,
          gas: web3.toHex(_gas),
          gasPrice: web3.toHex(defaultGasPrice),
          value: amountETHToSend,
          gasLimit: web3.toHex(_gasLimit)},
        next_callback);
    };

    processTx(0);
  };

};
