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

$('#secret_link').click(function() {
  let is_checked = $(this).is(':checked');

  $('.to_name').toggleClass('hidden');
});

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
  $('.cb-value').click(function() {
    var mainParent = $(this).parent('.toggle-btn');

    if ($(mainParent).find('input.cb-value').is(':checked')) {

      var username = $('.username-search').select2('data')[0] ? $('.username-search').select2('data')[0].text : '';
      const url = '/tip/address/' + username;

      fetch(url, {method: 'GET', credentials: 'include'}).then(function(response) {
        return response.json();
      }).then(function(json) {
        if (json.addresses.length > 0 && json.addresses[0] !== '0x0') {
          $('#send-stream-invite').css('display', 'none');
          var validToken = validateStreamingToken();

          if (!validToken) {
            $(mainParent).find('input.cb-value').prop('checked', false);
            _alert('The token you selected is not valid for streaming', 'error');
          } else {
            var proxyAddress = sablier_proxy_address();

            if (!proxyAddress.startsWith('0x')) {
              $(mainParent).find('input.cb-value').prop('checked', false);
              _alert('Streaming tips is not available on this network', 'error');
            } else {
              $(mainParent).addClass('active');
              $('#sablier-opts').css('display', 'block');
            }
          }
        } else {
          _alert({ message: gettext('Recipient does not have any payment address set. Click in the button below if you want to send an invite') }, 'warning');
          $('#send-stream-invite').css('display', 'inline-block');
        }
      });
    } else {
      $(mainParent).removeClass('active');
      $('#sablier-opts').css('display', 'none');
    }
  });
  $('#duration').durationPicker({
    lang: 'en',
    onChanged: function(time) {
      var tokenAddress = $('#token').val();

      if (tokenAddress && tokenAddress != '0x0') {
        var token = tokenAddressToDetails(tokenAddress);
        var amount = parseFloat($('#amount').val());
        var streamTime = parseInt(time);

        if (amount > 0 && streamTime > 0) {
          var deposit = getEffectiveStreamDeposit(amount, token.decimals, streamTime);
          var streamPerSec = deposit.div(web3.toBigNumber(time)).div(web3.toWei(web3.toBigNumber(1), 'ether')).toNumber();
          var text = `It will stream ${streamPerSec >= 0.001 ? `~${streamPerSec.toFixed(3)}` : '<0.001'} ${token.name} / sec`;

          $('#stream-per-sec').html(text);
        } else {
          $('#stream-per-sec').html('</br>');
        }
      }
    },
    showSeconds: false
  });
  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
  $('#send').on('click', function(e) {
    e.preventDefault();
    if ($(this).hasClass('disabled'))
      return;

    // get form data
    var email = $('#email').val();
    var github_url = $('#issueURL').val();
    var from_name = $('#fromName').val();
    var username = $('.username-search').select2('data')[0] ? $('.username-search').select2('data')[0].text : '';
    var amount = parseFloat($('#amount').val());
    var comments_priv = $('#comments_priv').val();
    var comments_public = $('#comments_public').val();
    var from_email = $('#fromEmail').val();
    var accept_tos = $('#tos').is(':checked');
    var secret_link = $('#secret_link').is(':checked');
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

    if (!username && !secret_link) {
      _alert('Please enter a recipient', 'error');
      return;
    }

    var stream = $('input.cb-value').is(':checked');
    var time = parseInt($('#duration').val());

    if (stream && !validateStreamingToken()) {
      _alert('The token you selected is not valid for streaming', 'error');
      return;
    }
    if (stream && time <= 0) {
      _alert('Please enter a valid time for streaming your tip', 'error');
      return;
    }

    var success_callback = function(txid, streamid) {

      startConfetti();
      var url = 'https://' + etherscanDomain() + '/tx/' + txid;

      var message = 'This transaction has been sent 👌';

      if (streamid) {
        var payerURL = get_sablier_url(streamid, false);

        message = `Your streaming money has been created with ID <a href="${payerURL}" target="_blank" rel="noopener noreferrer">${streamid}</a> 💸`;
        $('#stream_payee_info').css('display', 'block');
        $('#sablier-payee-url').attr('href', get_sablier_url(streamid, true));
      }
      $('#loading_trans').html(message);
      $('#send_eth').css('display', 'none');
      $('#send_eth_done').css('display', 'block');
      $('#tokenName').html(tokenName);
      $('#new_username').html(username);
      $('#trans_link').attr('href', url);
      $('#trans_link2').attr('href', url);
      unloading_button($(this));
      dataLayer.push({
        'event': 'sendtip',
        'category': 'sendtip',
        'action': 'sendtip'
      });
    };
    var failure_callback = function() {
      unloading_button($('#send'));
    };

    loading_button($(this));

    return sendTip(email, github_url, from_name, username, amount, stream ? time : 0, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, false);

  });

  $('#send-stream-invite').on('click', function(e) {
    e.preventDefault();

    var username = $('.username-search').select2('data')[0] ? $('.username-search').select2('data')[0].text : '';
    var from_email = $('#fromEmail').val();

    if (!username) {
      _alert('Please enter a recipient', 'error');
      return;
    }

    loading_button($(this));

    var url = '/tip/invite';

    fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({
        username: username,
        from_email: from_email,
        network: document.web3network
      })
    }).then(function(response) {
      unloading_button($('#send-stream-invite'));
      $('#send-stream-invite').addClass('disabled');
      return response.json();
    }).then(function(json) {
      var is_success = json['status'] == 'OK';
      var _class = is_success ? 'info' : 'error';

      _alert(json['message'], _class);
    });

  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      if (ele && ele.addr) {
        const is_token_selected = $('#token').data('token') === ele.name ? ' selected' : ' ';
        const html = '<option value=' + ele.addr + is_token_selected + '>' + ele.name + '</option>';

        $('#token').append(html);
      }
    });
    $('#token').val('0x0000000000000000000000000000000000000000').select2();
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

function validateStreamingToken() {
  var tokenAddress = (
    ($('#token').val() == '0x0') ?
      '0x0000000000000000000000000000000000000000'
      : $('#token').val());
  // derived info
  var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
  var tokenDetails = tokenAddressToDetails(tokenAddress);
  // TODO: Extra validation: whitelisted tokens for streaming?

  return !isSendingETH;
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function getEffectiveStreamDeposit(amount, decimals, time) {
  var amountBN = web3.toBigNumber('1'.padEnd(decimals + 1, 0)).mul(web3.toBigNumber(amount * 1.0));

  return amountBN.sub(amountBN.mod(web3.toBigNumber(time)));
}

function transactionReceiptAsync(txHash, f) {
  var transactionReceipt = web3.eth.getTransactionReceipt(txHash, function(error, receipt) {
    if (receipt) {
      f(receipt);
    } else {
      setTimeout(() => transactionReceiptAsync(txHash, f), 1000);
    }
  });
}


function sendTip(email, github_url, from_name, username, amount, streamTime, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, is_for_bounty_fulfiller) {
  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
    failure_callback();
    return;
  }
  // setup
  web3.eth.getAccounts(function(error, accounts) {
    if (error) {
      _alert({ message: gettext('You must unlock & enable Gitcoin via your web3 wallet to continue.') }, 'warning');
      failure_callback();
      return;
    }

    const fromAccount = accounts[0] ? accounts[0] : document.web3_address;

    if (typeof fromAccount == 'undefined') {
      _alert({ message: gettext('You must unlock & enable Gitcoin via your web3 wallet to continue.') }, 'warning');
      failure_callback();
      return;
    }

    if (username.indexOf('@') == -1) {
      username = '@' + username;
    }

    var gas_multiplier = 1.008;
    var gas_money = parseInt(Math.pow(10, (9 + 5)) * ((get_gas_price() * gas_multiplier) / Math.pow(10, 9)));
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
    _alert({ message: gettext('Creating tip...') }, 'info', 5000);

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
          var finalize_tip_registry = function(txid, streamid) {
            const url = '/tip/send/4';

            // TODO: store some metadata about streaming through this method
            fetch(url, {
              method: 'POST',
              credentials: 'include',
              body: JSON.stringify({
                destinationAccount: destinationAccount,
                txid: txid,
                is_direct_to_recipient: is_direct_to_recipient,
                stream_id: streamid,
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
                success_callback(txid, streamid);
              }
            });

          };
          var post_send_callback = function(errors, txid) {
            indicateMetamaskPopup(true);
            if (errors) {
              _alert({ message: gettext('There was an error.') }, 'warning');
              failure_callback();
            } else {
              finalize_tip_registry(txid);
            }
          };

          if (isSendingETH) {
            indicateMetamaskPopup();
            web3.eth.sendTransaction({
              from: fromAccount,
              to: destinationAccount,
              value: amountInDenom
            }, post_send_callback);
          } else if (streamTime == 0) { // Normal tip
            var send_erc20 = function() {
              var token_contract = web3.eth.contract(token_abi).at(tokenAddress);

              indicateMetamaskPopup();
              token_contract.transfer(destinationAccount, amountInDenom, {}, post_send_callback);
            };
            var send_gas_money_and_erc20 = function() {
              _alert({ message: gettext('You will now be asked to confirm two transactions.  The first is gas money, so your receipient doesnt have to pay it.  The second is the actual token transfer. (note: check Metamask extension, sometimes the 2nd confirmation window doesnt popup)') }, 'info');
              web3.eth.sendTransaction({
                to: destinationAccount,
                value: gas_money
              }, send_erc20);
            };

            if (is_direct_to_recipient) {
              send_erc20();
            } else {
              send_gas_money_and_erc20();
            }
          } else { // Stream tip using Sablier
            var deposit = getEffectiveStreamDeposit(amount, tokenDetails.decimals, streamTime);
              
            if (is_direct_to_recipient) {
              var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
              var proxyAddress = sablier_proxy_address();
              var proxy_contract = web3.eth.contract(sablier_proxy_abi).at(proxyAddress);
              var recipient = metadata['direct_address'];
              var errorRaised = false;

              var post_stream_callback = function(errors, txid) {
                indicateMetamaskPopup(true);
                if (errors) {
                  if (!errorRaised) {
                    _alert({ message: gettext('There was an error. Failed to stream money') }, 'error');
                  }
                  failure_callback();
                } else {
                  _alert({ message: gettext('Creating stream... Please Do Not close this window until finished!') }, 'info');
                  proxy_contract.CreateSalary({ company: fromAccount }, function(error, event) {
                    if (!error) {
                      var streamid = event.args.salaryId.toNumber();

                      finalize_tip_registry(txid, streamid);
                    }
                  });
                }

              };
                
              // Execute approve tx
              token_contract.approve(proxyAddress, deposit, function(errors, txid) {
                if (errors) {
                  // indicateMetamaskPopup(true);
                  _alert({ message: gettext('There was an error. Token was not approved') }, 'error');
                  errorRaised = true;
                  failure_callback();
                }
              });

              // Create streaming
              var now = Math.round(new Date().getTime() / 1000);
              var time_delta = 300; // Delta of 5min
              var startTime = now + time_delta;
              var endTime = now + streamTime + time_delta;
              
              proxy_contract.createSalary(recipient, deposit, tokenAddress, startTime, endTime,
                post_stream_callback);
              _alert({ message: gettext("You will now be asked to confirm two transactions. The first is to approve a token allowance.  The second will create the stream. (note: for the 2nd Tx an error alert would appear. Please ignore it! If using Metamask, sometimes the 2nd confirmation window doesn't popup)") }, 'info');
              indicateMetamaskPopup();
              setTimeout(() => indicateMetamaskPopup(true), 5000);

            } else {
              // TODO: manage when recipient does not have an account.
              // ATM User can send an email when an account is not found when calling `/tip/address/'` (see below)
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
      } else if (streamTime == 0) {
        // pay out via secret sharing algo
        wait_for_metadata(got_metadata_callback);
      } else {
        _alert({ message: gettext('Recipient does not have any payment address set. Click in the button below if you want to send an invite') }, 'warning', 5000);
        $('#send-stream-invite').css('display', 'inline-block');
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
