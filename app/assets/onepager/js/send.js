/* eslint-disable no-console */
var get_gas_price = function() {
  if ($('#gasPrice').length) {
    return $('#gasPrice').val() * Math.pow(10, 9);
  }
  if (typeof defaultGasPrice != 'undefined') {
    return defaultGasPrice;
  }
  return 5 * 10 ** 9;
};

var generate_or_get_private_key = function() {
  if (typeof document.account != 'undefined') {
    return document.account;
  }
  document.account = new Accounts().new();
  document.account['shares'] = secrets.share(document.account['private'], 3, 2);
  return document.account;
};

var clear_metadata = function() {
  document.account = undefined;
  document.hash1 = undefined;
};

var set_metadata = function(callback) {
  var account = generate_or_get_private_key();
  var shares = account['shares'];

  ipfs.ipfsApi = IpfsApi(ipfsConfig);
  ipfs.setProvider(ipfsConfig);
  ipfs.add(shares[1], function(err, hash1) {
    if (err)
      throw err;
    document.hash1 = hash1;
  });
};
var wait_for_metadata = function(callback) {
  setTimeout(function() {
    if (typeof document.hash1 != 'undefined') {
      var account = generate_or_get_private_key();

      callback({
        'pub_key': account['public'],
        'address': account['address'],
        'reference_hash_for_receipient': document.hash1,
        'gitcoin_secret': account['shares'][0]
      });
    } else {
      wait_for_metadata(callback);
    }
  }, 500);

};

$(document).ready(function() {

  // upon keypress for the select2, gotta make sure it opens
  setTimeout(function() {
    $('.select2').keypress(function() {
      $(this).siblings('select').select2('open');
    });
  }, 100);

  if (typeof userSearch != 'undefined') {
    userSearch('.username-search', true);
  }
  set_metadata();
  // jquery bindings
  $('#advanced_toggle').on('click', function() {
    advancedToggle();
  });
  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
  $('#send').on('click', function(e) {
    e.preventDefault();
    if ($(this).hasClass('disabled'))
      return;
    loading_button($(this));
    // get form data
    var email = $('#email').val();
    var github_url = $('#issueURL').val();
    var from_name = $('#fromName').val();
    var username = $('.username-search').select2('data')[0].text;
    var amount = parseFloat($('#amount').val());
    var comments_priv = $('#comments_priv').val();
    var comments_public = $('#comments_public').val();
    var from_email = $('#fromEmail').val();
    var accept_tos = $('#tos').is(':checked');
    var tokenAddress = (
      ($('#token').val() == '0x0') ?
        '0x0000000000000000000000000000000000000000'
        : $('#token').val());
    var expires = parseInt($('#expires').val());

    // derived info
    var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
    var tokenDetails = tokenAddressToDetails(tokenAddress);
    var tokenName = 'ETH';

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
    var failure_callback = function() {
      unloading_button($('#send'));
    };

    return sendTip(email, github_url, from_name, username, amount, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, false);

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


function sendTip(email, github_url, from_name, username, amount, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, is_for_bounty_fulfiller) {
  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
    failure_callback();
    return;
  }
  // setup
  var fromAccount = web3.eth.accounts[0];

  if (typeof fromAccount == 'undefined') {
    _alert({ message: gettext('You must unlock & enable Gitcoin via your web3 wallet to continue.') }, 'warning');
    failure_callback();
    return;
  }

  if (username.indexOf('@') == -1) {
    username = '@' + username;
  }

  var gas_money = parseInt(Math.pow(10, (9 + 5)) * ((defaultGasPrice * 1.001) / Math.pow(10, 9)));
  var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
  var tokenDetails = tokenAddressToDetails(tokenAddress);
  var tokenName = 'ETH';
  var denomFactor = Math.pow(10, 18);
  var creation_time = Math.round((new Date()).getTime() / 1000);
  var salt = parseInt((Math.random() * 1000000));

  if (!isSendingETH) {
    tokenName = tokenDetails.name;
    denomFactor = Math.pow(10, tokenDetails.decimals);
  }

  check_balance_and_alert_user_if_not_enough(
    tokenAddress,
    amount,
    'You do not have enough ' + tokenName + ' to send this tip.');

  var amountInDenom = amount * 1.0 * denomFactor;
  // validation
  var hasEmail = email != '';

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
  if (!isNumeric(amountInDenom) || amountInDenom == 0) {
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

  var got_metadata_callback = function(metadata) {
    const url = '/tip/send/3';

    metadata['creation_time'] = creation_time;
    metadata['salt'] = salt;
    metadata['source_url'] = document.location.href;

    fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({
        username: username,
        email: email,
        tokenName: tokenName,
        amount: amount,
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
        metadata: metadata
      })
    }).then(function(response) {
      return response.json();
    }).then(function(json) {
      var is_success = json['status'] == 'OK';
      var _class = is_success ? 'info' : 'error';

      if (!is_success) {
        _alert(json['message'], _class);
        failure_callback();
      } else {
        var is_direct_to_recipient = metadata['is_direct'];
        var destinationAccount = is_direct_to_recipient ? metadata['direct_address'] : metadata['address'];
        var post_send_callback = function(errors, txid) {
          indicateMetamaskPopup(true);
          if (errors) {
            _alert({ message: gettext('There was an error.') }, 'warning');
            failure_callback();
          } else {
            const url = '/tip/send/4';

            fetch(url, {
              method: 'POST',
              credentials: 'include',
              body: JSON.stringify({
                destinationAccount: destinationAccount,
                txid: txid,
                is_direct_to_recipient: is_direct_to_recipient,
                creation_time: creation_time,
                salt: salt
              })
            }).then(function(response) {
              return response.json();
            }).then(function(json) {
              var is_success = json['status'] == 'OK';

              if (!is_success) {
                _alert(json, _class);
              } else {
                clear_metadata();
                set_metadata();
                success_callback(txid);
              }
            });
          }
        };

        indicateMetamaskPopup();
        if (isSendingETH) {
          web3.eth.sendTransaction({
            to: destinationAccount,
            value: amountInDenom,
            gasPrice: web3.toHex(get_gas_price())
          }, post_send_callback);
        } else {
          var send_erc20 = function() {
            var token_contract = web3.eth.contract(token_abi).at(tokenAddress);

            token_contract.transfer(destinationAccount, amountInDenom, {gasPrice: web3.toHex(get_gas_price())}, post_send_callback);
          };
          var send_gas_money_and_erc20 = function() {
            _alert({ message: gettext('You will now be asked to confirm two transactions.  The first is gas money, so your receipient doesnt have to pay it.  The second is the actual token transfer. (note: check Metamask extension, sometimes the 2nd confirmation window doesnt popup)') }, 'info');
            web3.eth.sendTransaction({
              to: destinationAccount,
              value: gas_money,
              gasPrice: web3.toHex(get_gas_price())
            }, send_erc20);
          };

          if (is_direct_to_recipient) {
            send_erc20();
          } else {
            send_gas_money_and_erc20();
          }

        }
      }
    });
  };

  // send direct, or not?
  const url = '/tip/address/' + username;

  fetch(url, {method: 'GET', credentials: 'include'}).then(function(response) {
    return response.json();
  }).then(function(json) {
    if (json.addresses.length > 0) {
      // pay out directly
      got_metadata_callback({
        'is_direct': true,
        'direct_address': json.addresses[0],
        'creation_time': creation_time,
        'salt': salt
      });
    } else {
      // pay out via secret sharing algo
      wait_for_metadata(got_metadata_callback);
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
