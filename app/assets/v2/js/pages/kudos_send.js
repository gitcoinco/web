/* eslint-disable no-console */

var get_gas_price = function() {
  if ($('#gasPrice').length) {
    return $('#gasPrice').val() * Math.pow(10, 9);
  }
  if (typeof defaultGasPrice != 'undefined') {
    return defaultGasPrice;
  }
  // 5 gwei
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

  console.log(ipfsConfig);
  ipfs.ipfsApi = IpfsApi(ipfsConfig);
  ipfs.setProvider(ipfsConfig);
  ipfs.add(shares[1], function(err, hash1) {
    if (err)
      throw err;
    document.hash1 = hash1;
  });
};

// Step 6
var wait_for_metadata = function(callback) {
  setTimeout(function() {
    if ((typeof document.hash1 != 'undefined') && (document.hash1 != null)) {
      console.log('document.hash1 = ' + document.hash1);
      var account = generate_or_get_private_key();

      // This is the metadata that gets passed into got_metadata_callback()
      callback({
        'pub_key': account['public'],
        'address': account['address'],
        'reference_hash_for_receipient': document.hash1,
        'gitcoin_secret': account['shares'][0],
        'is_direct': false
      });
    } else {
      console.log('still waiting...');
      // Step 7
      // Once the new account and key are generated, move onto got_metadata_callback()
      wait_for_metadata(callback);
    }
  }, 500);

};


var wait_for_metadata_test = function(callback) {
  // only for local testing purposes
  console.log('document.hash1 = ' + document.hash1);
  var account = generate_or_get_private_key();

  // This is the metadata that gets passed into got_metadata_callback()
  callback({
    'pub_key': account['public'],
    'address': account['address'],
    'reference_hash_for_receipient': document.hash1,
    'gitcoin_secret': account['shares'][0],
    'is_direct': false
  });
};


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
  } else if (document.web3network == 'ropsten') {
    // ropsten
    etherscanDomain = 'ropsten.etherscan.io';
  } else {
    // mainnet
  }
  return etherscanDomain;
};

var renderWallets = function(profileId) {
  // $('.form-check').remove()
  console.log('profileId: ' + profileId);
  let url = '/api/v0.1/wallet?profile_id=' + profileId;

  $.get(url, function(results, status) {
    console.log(status);
    results.forEach(function(r) {
      console.log(r);
      let walletAddress = r.address;

      let walletItem = document.createElement('div');

      $(walletItem).attr('class', 'form-check');

      let walletInput = document.createElement('input');

      $(walletInput).attr('class', 'form-check-input').attr('type', 'radio').
        attr('name', 'address').attr('value', walletAddress).attr('checked', 'true');

      let walletLabel = document.createElement('label');

      $(walletLabel).attr('class', 'form-check-label').attr('for', 'address').text(walletAddress);

      $(walletItem).append(walletInput, walletLabel);
      $('#username-fg').after(walletItem);
    });
  });
};

// START HERE
// Step 0
// DOM is ready
$(document).ready(function() {

  // upon keypress for the select2, gotta make sure it opens
  setTimeout(function() {
    $('.select2').keypress(function() {
      $(this).siblings('select').select2('open');
    });
  }, 100);

  set_metadata();
  // jquery bindings
  $('#advanced_toggle').on('click', function(e) {
    e.preventDefault();
    advancedToggle();
  });


  $('#tip_nav li').on('click', function(e) {
    e.preventDefault();
    $('#tip_nav li').removeClass('selected');
    $(this).addClass('selected');
    if ($(this).hasClass('github')) {
      $('.username .select2').removeClass('hidden');
      $('.eth_address').addClass('hidden');
      $('#airdrop_link').addClass('hidden');
      $('.redemptions').addClass('hidden');
      $('.redemptions select').val(1);
      $('input[name=send_type]').val('github');
    } else if ($(this).hasClass('airdrop')) {
      $('.username .select2').addClass('hidden');
      $('.redemptions').removeClass('hidden');
      $('.eth_address').addClass('hidden');
      $('#airdrop_link').removeClass('hidden');
      $('input[name=send_type]').val('airdrop');
    } else {
      $('.username .select2').addClass('hidden');
      $('.redemptions').addClass('hidden');
      $('.eth_address').removeClass('hidden');
      $('.redemptions select').val(1);
      $('#airdrop_link').addClass('hidden');
      $('input[name=send_type]').val('eth_address');
    }
  });


  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
  $('#username').select2();

  // Step 1
  // Kudos send button is clicked
  $('#send').on('click', function(e) {

    e.preventDefault();

    if (typeof web3 == 'undefined') {
      _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
      return;
    }
    if (!web3.eth.coinbase) {
      _alert({ message: gettext('Please unlock metamask.') }, 'warning');
      return;
    }
    var kudos_network = $('#kudosNetwork').val();

    if (document.web3network != kudos_network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ' + kudos_network) }, 'warning');
      return;
    }

    $('#send_eth')[0].checkValidity();

    if (!$('#username')[0].checkValidity()) {
      $('#username')[0].reportValidity();
    }
    var inputsValidate = document.querySelectorAll('input');

    inputsValidate.forEach(function(elem) {
      elem.reportValidity();
    });
    if ($(this).hasClass('disabled') || !$('#send_eth')[0].checkValidity())
      return;


    loading_button($(this));

    // Step 2
    // get form data
    var email = $('#email').val();
    var github_url = $('#issueURL').val();
    var from_name = $('#fromName').val();
    // should username be to_username for clarity?
    var username = '';

    if ($('#username').select2('data').length) {
      username = $('#username').select2('data')[0].text || $('#username').select2('data')[0];
    }
    var receiverAddress = $('#receiverAddress').val();
    var amountInEth = parseFloat($('#amount').val());
    var comments_priv = $('#comments_priv').val();
    var comments_public = $('#comments_public').val();
    var from_email = $('#fromEmail').val();
    var to_eth_address = $('#to_eth_address').val();
    var accept_tos = $('#tos').is(':checked');
    var expires = parseInt($('#expires').val());
    // kudosId is the kudos database id that is being cloned
    var kudosId = $('#kudosid').data('kudosid');
    // tokenId is the kudos blockchain id that is being cloned
    var tokenId = $('#tokenid').data('tokenid');
    var send_type = $('input[name=send_type]').val();
    var num_redemptions = $('.redemptions select').val();

    // get kudosPrice from the HTML
    kudosPriceInEth = parseFloat($('#kudosPrice').attr('data-ethprice'));
    kudosPriceInWei = new web3.BigNumber((kudosPriceInEth * 1.0 * Math.pow(10, 18)).toString());

    var formData = {
      email: email,
      github_url: github_url,
      from_name: from_name,
      username: username,
      receiverAddress: receiverAddress,
      // amountInEth is the kudos price in eth
      amountInEth: amountInEth,
      comments_priv: comments_priv,
      comments_public: comments_public,
      from_email: from_email,
      accept_tos: accept_tos,
      expires: expires,
      kudosId: kudosId,
      tokenId: tokenId,
      to_eth_address: to_eth_address,
      send_type: send_type
    };

    // derived info
    var tokenName = 'ETH';
    var weiConvert = Math.pow(10, 18);

    // Step 11 (LAST STEP)
    // Show the congragulation screen
    var success_callback = function(txid) {

      startConfetti();
      var url = 'https://' + etherscanDomain() + '/tx/' + txid;

      $('#loading_trans').html('This transaction has been sent 👌');
      $('#loading_trans').hide();
      $('#send_eth').css('display', 'none');
      $('#send_eth_done').css('display', 'block');
      if (username) {
        var username_html = "<a href='/profile/" + username + "'>" + username + '</a>';

        $('#new_username').html(username_html);
      } else if (to_eth_address) {
        $('#new_username').html(to_eth_address);
      } else {
        $('#send_eth_done .font-weight-300').remove();
        var cta_url = document.location.origin + document.airdrop_url;
        var link = "<a href='" + cta_url + "'>" + cta_url + '</a>';
        var num_times = $('.redemptions select').val();
        var num_times_plural = num_times > 1 ? 's' : '';

        $('#send_eth_done p.notifier').html('Your airdrop link is ' + link + '<br><br>This link is valid to be used *' + num_times + '* time' + num_times_plural + '.  Copy it and send it to whomever you want to receive the kudos.');
      }
      $('#trans_link').attr('href', url);
      $('#trans_link2').attr('href', url);
      unloading_button($(this));
    };
    var failure_callback = function() {
      unloading_button($('#send'));
    };

    kudosId = $('#kudosid').data('kudosid');
    tokenId = $('#tokenid').data('tokenid');
    // cloneAndTransferKudos(kudosId, 1, receiverAddress);
    // cloneKudos(kudosId, 1);

    // Step 3
    // Run sendKudos function
    return sendKudos(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, to_eth_address, expires, kudosId, tokenId, success_callback, failure_callback, false, send_type);

  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      if (ele && ele.addr) {
        var html = '<option value=' + ele.addr + '>' + ele.name + '</option>';

        $('#token').append(html);
      }
    });
    // jQuery('#token').select2();
  });

});

// Step 3
function sendKudos(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, to_eth_address, expires, kudosId, tokenId, success_callback, failure_callback, is_for_bounty_fulfiller, send_type) {

  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
    failure_callback();
    return;
  }
  // setup

  if (username && username.indexOf('@') == -1) {
    username = '@' + username;
  }
  var _disableDeveloperTip = true;
  var observedKudosGasLimit = 505552;
  var buffer_pct = 1.005;
  var wei_to_gwei = Math.pow(10, 9);
  var gas_money = parseInt((wei_to_gwei * observedKudosGasLimit) * (buffer_pct * defaultGasPrice / wei_to_gwei));
  var tokenName = 'ETH';
  var weiConvert = Math.pow(10, 18);
  var creation_time = Math.round((new Date()).getTime() / 1000);
  var salt = parseInt((Math.random() * 1000000));

  var amountInWei = amountInEth * 1.0 * weiConvert;
  // validation
  // console.log(amountInEth)
  // console.log(amountInWei)
  var hasEmail = email != '';
  var hasUsername = username != '';

  // Step 4
  // validation
  console.log(send_type);
  if (send_type != 'airdrop' && !username && !to_eth_address) {
    _alert({ message: gettext('You must specify a recipient.') }, 'warning');
    failure_callback();
    return;
  }
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
    _alert({ message: gettext('You must enter a number for the amount!') }, 'warning');
    failure_callback();
    return;
  }
  if (!accept_tos) {
    _alert({ message: gettext('You must accept the terms.') }, 'warning');
    failure_callback();
    return;
  }

  // warnings
  if (username == $('#fromName').val()) {
    _alert({ message: gettext('Kudos are intended to be compliments. just like you *can* give yourself a compliment or *can* give yourself an award, you are also able to send yourself a Kudos. ') }, 'warning');
  }


  // console.log('got to metadata_callback')

  // Step 7
  // Do a POST request to the kudos/send/3
  // This adds the information to the kudos_transfer table
  // Then the metamask transaction gets kicked off
  // Once the transaction is mined, the txid is added to the database in kudos/send/4
  // function inside of getKudos()
  var got_metadata_callback = function(metadata) {
    const url = '/kudos/send/3/';

    metadata['creation_time'] = creation_time;
    metadata['salt'] = salt;
    metadata['source_url'] = document.location.href;
    metadata['direct_eth_send'] = false;
    if (to_eth_address) {
      metadata['address'] = to_eth_address;
      metadata['direct_eth_send'] = true;
    }


    var num_redemptions = 1;

    if ($('.redemptions select').length) {
      num_redemptions = $('.redemptions select').val();
    }
    var formbody = {
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
      to_eth_address: to_eth_address,
      kudosId: kudosId,
      tokenId: tokenId,
      network: document.web3network,
      from_address: web3.eth.coinbase,
      is_for_bounty_fulfiller: is_for_bounty_fulfiller,
      metadata: metadata,
      send_type: send_type,
      num_redemptions: num_redemptions
    };

    if (send_type == 'airdrop') {
      formbody['pk'] = document.account['private'];
    }


    fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify(formbody)
    }).then(function(response) {
      // console.log(response)
      return response.json();
    }).then(function(json) {
      var is_success = json['status'] == 'OK';
      var _class = is_success ? 'info' : 'error';

      if (!is_success) {
        _alert(json['message'], _class);
        failure_callback();
      } else {
        // Step 8
        // A json object with SUCCESS is received from the back-end
        var is_direct_to_recipient = metadata['is_direct'] || to_eth_address;
        var destinationAccount = to_eth_address ? to_eth_address : metadata['address'];

        if (json['url']) {
          document.airdrop_url = json['url'];
        }

        var post_send_callback = function(errors, txid, kudos_id) {
          indicateMetamaskPopup(true);
          if (errors) {
            _alert({ message: gettext('There was an error.') }, 'warning');
            failure_callback();
          } else {
            const url = '/kudos/send/4/';

            fetch(url, {
              method: 'POST',
              credentials: 'include',
              body: JSON.stringify({
                destinationAccount: destinationAccount,
                txid: txid,
                kudos_id: kudos_id,
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
                // Step 11
                // LAST STEP
                success_callback(txid);
              }
            });
          }
        };
        // end post_send_callback

        // Pull up Kudos contract instance
        var kudos_contract = web3.eth.contract(kudos_abi).at(kudos_address());

        var numClones = 1;
        var account = web3.eth.coinbase;

        console.log('destinationAccount:' + destinationAccount);

        var kudosPriceInEth = parseFloat($('#kudosPrice').attr('data-ethprice')) || $('.kudos-search').select2('data')[0].price_finney;
        var kudosPriceInWei = new web3.BigNumber((kudosPriceInEth * 1.0 * Math.pow(10, 18)).toString());

        if (is_direct_to_recipient) {
          // Step 9
          // Kudos Direct Send (KDS)
          console.log('Using Kudos Direct Send (KDS)');


          kudos_contract.clone(destinationAccount, tokenId, numClones, {from: account, value: kudosPriceInWei, gasPrice: web3.toHex(get_gas_price())
          }, function(cloneError, cloneTxid) {
            // getLatestId yields the last kudos_id
            kudos_contract.getLatestId(function(error, kudos_id) {
              post_send_callback(cloneError, cloneTxid, kudos_id);
            });
          });

          // Send Indirectly
        } else {
          // Step 9
          // Kudos Indirect Send (KIS)
          // estimate gas for cloning the kudos
          console.log('Using Kudos Indirect Send (KIS)');

          params = {
            tokenId: tokenId,
            numClones: numClones,
            from: account,
            value: kudosPriceInWei.toString()
          };

          kudos_contract.clone.estimateGas(destinationAccount, tokenId, numClones, {from: account, value: kudosPriceInWei, gasPrice: web3.toHex(get_gas_price())
          }, function(err, kudosGasEstimate) {
            if (err) {
              unloading_button($('#send'));
              _alert('Got an error back from RPC node.  Please try again or contact support');
              throw (err);
            }

            console.log('kudosGasEstimate: ' + kudosGasEstimate);
            // Multiply gas * gas_price_gwei to get gas cost in wei.
            kudosGasEstimateInWei = kudosGasEstimate * get_gas_price();
            _alert({ message: gettext('You will now be asked to confirm a transaction to cover the cost of the Kudos and the gas money.') }, 'info');
            money = {
              gas_money: gas_money,
              kudosGasEstimateInWei: kudosGasEstimateInWei,
              kudosPriceInWei: kudosPriceInWei.toNumber()
            };
            console.log(money);
            indicateMetamaskPopup();
            var num_redemptions = 1;

            if ($('.redemptions select').length) {
              num_redemptions = $('.redemptions select').val();
            }
            var total_send = ((gas_money + kudosGasEstimateInWei + kudosPriceInWei.toNumber()) * new web3.BigNumber(num_redemptions)).toString();

            web3.eth.sendTransaction({
              to: destinationAccount,
              // Add gas_money + gas cost for kudos contract transaction + cost of kudos token (Gitcoin keeps this amount?)
              value: total_send,
              gasPrice: web3.toHex(get_gas_price())
            }, post_send_callback);
          });
        }
      }
    });
  };

  // send direct, or not?
  const url = '/kudos/address/' + username;

  // Step 5
  // Check if we are sending direct or not
  // In the case of no kudos wallets, this will fail, move onto Step 6
  fetch(url, {method: 'GET', credentials: 'include'}).then(function(response) {
    return response.json();
  }).then(function(json) {
    if (json.addresses.length > 0) {
      // pay out directly
      got_metadata_callback({
        'is_direct': true,
        'address': json.addresses[0],
        'creation_time': creation_time,
        'salt': salt
      });
    } else {
      console.log('waiting for metadata');
      // pay out via secret sharing algo
      // Step 6
      wait_for_metadata(got_metadata_callback);
    }
  });
}

// web3.currentProvider.publicConfigStore.on('update', function(e) {
var error;

window.ethereum.publicConfigStore.on('update', checkNetwork);
function checkNetwork(e) {
  if (error) {
    return;
  }

  var network = e ? e.networkVersion : web3.version.network;

  console.log(web3.currentProvider);
  if (network === '4' || network === '1') {
    console.log(network);
  } else {
    error = true;
    _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
  }
}
checkNetwork();
