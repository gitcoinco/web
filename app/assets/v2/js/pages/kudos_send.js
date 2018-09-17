/* eslint-disable no-console */

var ethToWei = function(amountInEth) {
  // Accept a float value in eth and convert to Wei.
  let weiConvert = Math.pow(10, 18);
  return new web3.BigNumber(amountInEth * 1.0 * weiConvert);
}

var weiToEth = function(amountInWei) {
  // Accept a wei integer value and convert to a float Eth value.
  let weiConvert = Math.pow(10, 18);
  return amountInWei / weiConvert;
}

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
    if (typeof document.hash1 != 'undefined') {
      console.log('document.hash1 = ' + document.hash1)
      var account = generate_or_get_private_key();

      // This is the metadata that gets passed into got_metadata_callback()
      callback({
        'pub_key': account['public'],
        'address': account['address'],
        'reference_hash_for_receipient': document.hash1,
        'gitcoin_secret': account['shares'][0]
      });
    } else {
      console.log('still waiting...')
      // Step 7
      // Once the new account and key are generated, move onto got_metadata_callback()
      wait_for_metadata(callback);
    }
  }, 500);

};


var wait_for_metadata_test = function(callback) {
  console.log('document.hash1 = ' + document.hash1)
  var account = generate_or_get_private_key();

  // This is the metadata that gets passed into got_metadata_callback()
  callback({
    'pub_key': account['public'],
    'address': account['address'],
    'reference_hash_for_receipient': document.hash1,
    'gitcoin_secret': account['shares'][0]
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
  } else {
    // mainnet
  }
  return etherscanDomain;
};

var renderWallets = function (profileId) {
  // $('.form-check').remove()
  console.log('profileId: ' + profileId);
  let url = '/api/v0.1/wallet?profile_id=' + profileId;
  $.get(url, function(results, status) {
    console.log(status);
    results.forEach(function(r) {
      console.log(r);
      let walletAddress = r.address;

      let walletItem = document.createElement('div');
      $(walletItem).attr('class', 'form-check')

      let walletInput = document.createElement('input');
      $(walletInput).attr('class', 'form-check-input').attr('type', 'radio').
      attr('name', 'address').attr('value', walletAddress).attr('checked', 'true');

      let walletLabel = document.createElement('label');
      $(walletLabel).attr('class', 'form-check-label').attr('for', 'address').text(walletAddress);

      $(walletItem).append(walletInput, walletLabel);
      $('#username-fg').after(walletItem);
    })
  })
}

// START HERE
// Step 0
// DOM is ready
$(document).ready(function() {
  set_metadata();
  // jquery bindings
  $('#advanced_toggle').click(function(e) {
    e.preventDefault();
    advancedToggle();
  });
  $('#amount').on('keyup blur change', updateEstimate);
  $('#token').on('change', updateEstimate);
  $('#username').select2();
  // $('#username').on('select2:select', function(e) {
  //   let profileId = e.params.data.id;
  //   console.log(e.params.data)
  //   renderWallets(profileId);
  // });

  // Step 1
  // Kudos send button is clicked
  $('#send').click(function(e) {
    e.preventDefault();
    $('#send_eth')[0].checkValidity()

    if (!$('#username')[0].checkValidity() ) {
      $('#username')[0].reportValidity()
    }
    var inputsValidate = document.querySelectorAll('input')

    inputsValidate.forEach( function(elem){
      elem.reportValidity()
    })
    if ($(this).hasClass('disabled') || !$('#send_eth')[0].checkValidity() )
      return;


    loading_button($(this));

    if ($('#username').select2('data')[0] && $('#username').select2('data')[0].text) {
      var username = $('#username').select2('data')[0].text;
    } else {
      var username = undefined
    }

    // Step 2
    // get form data
    var email = $('#email').val();
    var github_url = $('#issueURL').val();
    var from_name = $('#fromName').val();
    // should username be to_username for clarity?
    // var username = $('#username').select2('data')[0].text || $('#username').select2('data')[0];
    var receiverAddress = $('#receiverAddress').val();
    var amountInEth = parseFloat($('#amount').val());
    var comments_priv = $('#comments_priv').val();
    var comments_public = $('#comments_public').val();
    var from_email = $('#fromEmail').val();
    var accept_tos = $('#tos').is(':checked');
    var tokenAddress = $('#token').val();
    var expires = parseInt($('#expires').val());
    // kudosName is the name of the kudos token that is being cloned
    var kudosName = window.location.href.split('\=')[1];

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
      tokenAddress: tokenAddress,
      expires: expires,
      kudosName: kudosName
    }

    // derived info
    var isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
    var tokenDetails = tokenAddressToDetails(tokenAddress);
    var tokenName = 'ETH';

    var weiConvert = Math.pow(10, 18);

    // if (!isSendingETH) {
    //   tokenName = tokenDetails.name;
    // }

    // Step 11 (LAST STEP)
    // Show the congragulation screen
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

    // var kudosName = $('#kudosImage').attr('alt');
    var kudosName = window.location.href.split('\=')[1];
    // cloneAndTransferKudos(kudosName, 1, receiverAddress);
    // cloneKudos(kudosName, 1);
    console.log(formData);
    // Step 3
    // Run sendKudos function
    return sendKudos(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, kudosName, success_callback, failure_callback, false);

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
function sendKudos(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, kudosName, success_callback, failure_callback, is_for_bounty_fulfiller) {
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
  // var tokenName = window.location.href.split('\=')[1];
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
  if (username == '' || username === undefined ) {
    _alert({ message: gettext('You must enter a username.') }, 'warning');
    failure_callback();
    return;
  }
  if (!accept_tos) {
    _alert({ message: gettext('You must accept the terms.') }, 'warning');
    failure_callback();
    return;
  }
  // console.log('got to metadata_callback')

  // Step 7
  // Do a POST request to the kudos/send/3
  // This adds the information to the kudos_email table
  // Then the metamask transaction gets kicked off
  // Once the transaction is mined, the txid is added to the database in kudos/send/4
  // function inside of getKudos()
  var got_metadata_callback = function(metadata) {
    const url = '/kudos/send/3/';

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
        amount: amountInEth,
        comments_priv: comments_priv,
        comments_public: comments_public,
        expires_date: expires,
        github_url: github_url,
        from_email: from_email,
        from_name: from_name,
        tokenAddress: tokenAddress,
        kudosName: kudosName,
        network: document.web3network,
        from_address: fromAccount,
        is_for_bounty_fulfiller: is_for_bounty_fulfiller,
        metadata: metadata
      })
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
        var is_direct_to_recipient = metadata['is_direct'];
        var destinationAccount = is_direct_to_recipient ? metadata['direct_address'] : metadata['address'];

        var post_send_callback = function(errors, txid) {
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
        var kudosContractInstance = web3.eth.contract(kudos_abi).at(kudos_address());

        if (isSendingETH) {
          alert(amountInWei);
          web3.eth.sendTransaction({
            to: destinationAccount,
            value: amountInWei,
            gasPrice: web3.toHex(get_gas_price())
          }, post_send_callback);
        } else {
          var send_kudos = function(name, numClones, receiver) {
            let account = web3.eth.coinbase;
            // let value = new web3.BigNumber(1000000000000000);
            let amountInEth = parseFloat($('#kudosPrice').attr('data-ethprice'))
            console.log(amountInEth)
            let weiConvert = Math.pow(10, 18);
            let value = new web3.BigNumber(amountInEth * 1.0 * weiConvert);
            console.log(value)
            console.log(value.toNumber())
            console.log(value.toString(10))
            kudosContractInstance.cloneAndTransfer(name, numClones, receiver, {from: account, value: value}, post_send_callback);

            // Step 10
            // call the post_send_callback() function which hits the /kudos/send/4 endpoint and updates
            // the database with the txid once it is mined.
            // token_contract.transfer(destinationAccount, amountInWei, {gasPrice: web3.toHex(get_gas_price())}, post_send_callback);
          };
          // This is what runs in the Kudos case
          var send_kudos_money = function(kudosGasEstimateInWei, kudosPriceInWei) {
            _alert({ message: gettext('You will now be asked to confirm a transaction to cover the cost of the Kudos and the gas money.') }, 'info');
            money = {
              gas_money: gas_money,
              kudosGasEstimateInWei: kudosGasEstimateInWei,
              kudosPriceInWei: kudosPriceInWei
            }
            console.log(money)
            web3.eth.sendTransaction({
              to: destinationAccount,
              // Add gas_money + gas cost for kudos contract transaction + cost of kudos token (Gitcoin keeps this amount?)
              value: gas_money + kudosGasEstimateInWei + kudosPriceInWei,
              gasPrice: web3.toHex(get_gas_price())
            }, post_send_callback);
          };


          if (is_direct_to_recipient) {
            // Step 9
            // Kudos Direct Send (KDS)
            console.log('Using Kudos Direct Send (KDS)');
            console.log('destinationAccount:' + destinationAccount);
            send_kudos(kudosName, 1, destinationAccount);

          } else {
            // Step 9
            // Kudos Indirect Send (KIS)
            // estimate gas for cloning the kudos
            console.log('Using Kudos Indirect Send (KIS)')
            var numClones = 1;
            let account = web3.eth.coinbase;
            let amountInEth = parseFloat($('#kudosPrice').attr('data-ethprice')); 
            let weiConvert = Math.pow(10, 18);
            // kudosCost is the price of the kudos in the send page.
            // var kudosPriceInWei = new web3.BigNumber(amountInEth * 1.0 * weiConvert);
            var kudosPriceInWei = amountInEth * 1.0 * weiConvert;
            // let value = new web3.BigNumber(1000000)
            params = {
              kudosName: kudosName,
              numClones: numClones,
              account: account,
              amountInEth: amountInEth,
              kudosPriceInWei: kudosPriceInWei
            }
            console.log(params)
            kudosContractInstance.clone.estimateGas(kudosName, numClones, {from: account, value: kudosPriceInWei}, function(error, kudosGasEstimate){
              console.log('kudosGasEstimate: '+ kudosGasEstimate)
              // Multiply gas * gas_price_gwei to get gas cost in wei.
              kudosGasEstimateInWei = kudosGasEstimate * get_gas_price();
              send_kudos_money(kudosGasEstimateInWei, kudosPriceInWei);
            });
          }
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
        'direct_address': json.addresses[0],
        'creation_time': creation_time,
        'salt': salt
      });
    } else {
      console.log('waiting for metadata')
      // pay out via secret sharing algo
      // Step 6
      // wait_for_metadata(got_metadata_callback);
      wait_for_metadata(got_metadata_callback);
      // let metadata = {}
      // got_metadata_callback(metadata);
    }
  });
}
