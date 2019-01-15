/* eslint-disable no-console */

var is_metamask_approved = is_metamask_approved || false;
var is_metamask_unlocked = is_metamask_unlocked || false;

function metamaskApproval() {
  window.web3 = new Web3();

  if (window.ethereum) {
    window.web3.setProvider(window.ethereum);
    window.ethereum._metamask.isApproved().then(
      function(res) {
        is_metamask_approved = res;
        if (!res) {
          ask_metamask_connection();
        }
      }
    );
    window.ethereum._metamask.isUnlocked().then(
      function(res) {
        is_metamask_unlocked = res;
      }
    );
  }
}

window.addEventListener('load', metamaskApproval);

function approveMetamask() {
  if (!window.ethereum) {
    return;
  }

  window.ethereum.enable().then(
    function(accounts) {
      is_metamask_approved = true;
      is_metamask_unlocked = true;
    }
  ).catch(
    function() {
      _alert(
        gettext('Permission to connect to MetaMask rejected.') +
        gettext('Please allow Gitcoin to connect to MetaMask.'),
        'warning'
      );
    }
  );
}

function ask_metamask_connection() {
  const shown_on = [ '/tip', '/kudos/send', '/ens' ];
  const page_url = window.location.pathname;
  let showBanner = false;

  for (let path of shown_on) {
    if (page_url.startsWith(path)) {
      showBanner = true;
      break;
    }
  }

  if (showBanner && !is_metamask_approved) {
    _alert(
      {
        message: gettext('MetaMask is not connected.') +
          '<button id="metamask_connect" onclick="approveMetamask()">' +
          gettext('Click here to connect to MetaMask') +
          '</button>'
      },
      'error'
    );
    $('#metamask_connect').css('background', 'none');
    $('#metamask_connect').css('color', 'white');
    $('#metamask_connect').css('border', '2px solid white');
    $('#metamask_connect').css('border-radius', '10px');
    $('#metamask_connect').css('margin-left', '8px');
  }
}

function sign_and_send(rawTx, success_callback, private_key) {
  // sign & serialize raw transaction
  console.log('rawTx: ' + JSON.stringify(rawTx));
  console.log('private_key: ' + private_key);
  var tx = new EthJS.Tx(rawTx);

  tx.sign(new EthJS.Buffer.Buffer.from(private_key, 'hex'));
  var serializedTx = tx.serialize();

  // send raw transaction
  const params = ['0x' + serializedTx.toString('hex')];
  const method = 'eth_sendRawTransaction';

  console.log(params);
  window.web3.currentProvider.sendAsync(
    {
      method,
      params
    },
    function(error, result) {
      const txid = result ? result['result'] : undefined;

      success_callback(error, txid);
    }
  );
}

/**
 * Looks for a transaction receipt.  If it doesn't find one, it keeps running until it does.
 * @callback
 * @param {string} txhash - The transaction hash.
 * @param {function} f - The function passed into this callback.
 */
var callFunctionWhenTransactionMined = function(txHash, f) {
  window.web3.eth.getTransactionReceipt(txHash).then(
    function(result) {
      if (result) {
        f();
      } else {
        setTimeout(function() {
          callFunctionWhenTransactionMined(txHash, f);
        }, 10000);
      }
    }
  ).catch(
    function() {
      setTimeout(function() {
        callFunctionWhenTransactionMined(txHash, f);
      }, 10000);
    }
  );
};

function waitForWeb3(callback) {
  if (window.web3 && (!window.web3.currentProvider || document.web3network)) {
    callback();
  } else {
    setTimeout(function() {
      waitForWeb3(callback);
    }, 100);
  }
}

function currentNetwork(network) {
  document.web3network = network;
  $('.navbar-network').removeClass('hidden');

  let tooltip_info = '';
  let currentNetwork = '';

  if (network === 'mainnet') {
    currentNetwork = 'Main Ethereum Network';
  }

  if (network === 'rinkeby') {
    currentNetwork = 'Rinkeby Network';
  }

  if (currentNetwork) {
    is_metamask_unlocked = true;

    $('#current-network').text(currentNetwork);
    $('.navbar-network').attr('title', '');
    $('.navbar-network i').addClass('green');
    $('.navbar-network i').removeClass('red');
    $('#navbar-network-banner').removeClass('network-banner--warning');
    $('#navbar-network-banner').addClass('hidden');
    return;
  }
  
  if (!network) {
    info = gettext('Web3 disabled. Please install ') +
      '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">MetaMask</a>';
    $('#current-network').text(gettext('MetaMask Not Enabled'));
    $('#navbar-network-banner').html(info);
  } else if (network === 'locked') {
    if (is_metamask_approved) {
      info = gettext('Web3 locked. Please unlock ') +
        '<a href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral" target="_blank" rel="noopener noreferrer">MetaMask</a>';
      $('#current-network').text(gettext('MetaMask Locked'));
      $('#navbar-network-banner').html(info);
    } else {
      info = gettext('MetaMask not connected. ') +
        '<button id="metamask_connect" onclick="approveMetamask()">Click here to connect to MetaMask</button>';
      $('#current-network').text(gettext('MetaMask Not Connected'));
      $('#navbar-network-banner').html(info);
    }
  } else {
    info = gettext('Connect to Mainnet or Rinkeby via MetaMask');
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

var trigger_primary_form_web3_hooks = function() {
  // detect web3, and if not, display a form telling users they must be web3 enabled.
  const isFaucet = $('#faucet_form').length > 0;

  if (isFaucet) {
    $('#ethAddress').val(document.coinbase);
    faucet_amount = parseInt($('#currentFaucet').val() * (Math.pow(10, 18)));
  }

  if ($('#primary_form').length || isFaucet) {
    const is_zero_balance_not_okay = !isFaucet;

    if (!window.web3.currentProvider) {
      $('#no_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');

      if (isFaucet) {
        $('#faucet_form').addClass('hidden');
      }
    } else if (is_metamask_unlocked && !is_metamask_approved) {
      $('#connect_metamask_error').css('display', 'block');
      $('#unlock_metamask_error').css('display', 'none');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');

      if (isFaucet) {
        $('#over_balance_error').css('display', 'none');
        $('#faucet_form').addClass('hidden');
      }
    } else if (!document.coinbase) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('#connect_metamask_error').css('display', 'none');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');

      if (isFaucet) {
        $('#over_balance_error').css('display', 'none');
        $('#faucet_form').addClass('hidden');
      }
    } else if (is_zero_balance_not_okay && document.balance == 0) {
      $('#zero_balance_error').css('display', 'block');
      $('#robot_error').removeClass('hidden');
      $('#primary_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
    } else if (isFaucet && (document.balance * Math.pow(10, 18)) >= faucet_amount) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#over_balance_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
    } else {
      $('#zero_balance_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'block');
      $('#robot_error').addClass('hidden');
      $('#primary_form').removeClass('hidden');
      $('.submit_bounty .newsletter').removeClass('hidden');
    }
  }
};

function trigger_form_hooks() {
  trigger_primary_form_web3_hooks();
}

function getNetwork(id) {
  const networks = {
    '1': 'mainnet',
    '2': 'morden',
    '3': 'ropsten',
    '4': 'rinkeby',
    '42': 'kovan'
  };

  return networks[id] || 'custom network';
}

function web3Unavailable(err) {
  currentNetwork();
  trigger_form_hooks();
}

function web3Locked() {
  currentNetwork('locked');
  trigger_form_hooks();
}

// figure out what version of web3 this is, whether we're logged in, etc..
function listen_for_web3_changes() {
  if (document.location.pathname.indexOf('grants') !== -1) {
    return;
  }

  if (!document.listen_for_web3_iterations) {
    document.listen_for_web3_iterations = 1;
  } else {
    document.listen_for_web3_iterations += 1;
  }

  if (!window.web3 || !window.web3.currentProvider) {
    web3Unavailable();
    return;
  }
  
  window.web3.eth.getCoinbase().then(
    function(coinbase) {
      if (!coinbase) {
        web3Locked();
        return;
      }

      document.coinbase = coinbase;
      is_metamask_unlocked = true;
      is_metamask_approved = true;

      window.web3.eth.getBalance(coinbase).then(
        function(result) {
          if (result) {
            document.balance = parseFloat(window.web3.utils.fromWei(result));
          }

          trigger_form_hooks();
        }
      ).catch(web3Unavailable);

      window.web3.eth.net.getId().then(
        function(netId) {
          const network = getNetwork(netId);

          currentNetwork(network);
          trigger_form_hooks();
        }
      ).catch(web3Unavailable);
    }
  ).catch(web3Unavailable);
}

window.addEventListener('load',
  function() {
    setInterval(listen_for_web3_changes, 1000);
  }
);
