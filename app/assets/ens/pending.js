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

function getNetwork(id) {
  var networks = {
    '1': 'mainnet',
    '2': 'morden',
    '3': 'ropsten',
    '4': 'rinkeby',
    '42': 'kovan'
  };

  return networks[id] || 'custom network';
}

// figure out what version of web3 this is
window.addEventListener('load', function() {
  var timeout_value = 100;

  setTimeout(function() {
    if (typeof web3 != 'undefined') {
      web3.version.getNetwork(function(error, netId) {
        if (!error) {
          document.web3network = getNetwork(netId);
        }
      });
    }
  }, timeout_value);
});

var ts = function() {
  return Math.round((new Date()).getTime() / 1000);
};

if (typeof localStorage['ts'] == 'undefined' || parseInt(localStorage['ts']) < (ts() - 3600)) {
  localStorage['ts'] = ts();
  localStorage['target_ts'] = ts() + (60 * 3); // 3 mins
}

setInterval(function() {
  var delta = parseInt(localStorage['target_ts']) - ts();
  var text = delta > 0 ? parseInt(delta) + ' seconds' : 'any minute now';

  jQuery('#timeestimate').text('estimated confirmation time: ' + text);
}, 1000);

var callFunctionWhenTransactionMined = function(txHash, f) {
  var transactionReceipt = web3.eth.getTransactionReceipt(txHash, function(error, result) {
    if (result) {
      f();
    } else {
      setTimeout(function() {
        callFunctionWhenTransactionMined(txHash, f);
      }, 10000);
    }
  });
};

callFunctionWhenTransactionMined($('#txn_hash').attr('value'), function() {
  location.reload(1);
});
