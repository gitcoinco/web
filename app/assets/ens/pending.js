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

// figure out what version of web3 this is
window.addEventListener('load', function() {
  var timeout_value = 100;

  setTimeout(function() {
    if (typeof web3 != 'undefined') {
      web3.version.getNetwork((error, netId) => {
        if (!error) {

          // figure out which network we're on
          var network = 'unknown';

          switch (netId) {
            case '1':
              network = 'mainnet';
              break;
            case '2':
              network = 'morden';
              break;
            case '3':
              network = 'ropsten';
              break;
            case '4':
              network = 'rinkeby';
              break;
            case '42':
              network = 'kovan';
              break;
            default:
              network = 'custom network';
          }
          document.web3network = network;
        }
      });
    }
  }, timeout_value);
});


var callFunctionWhenTransactionMined = function(txHash, f) {
  var transactionReceipt = web3.eth.getTransactionReceipt(txHash, function(error, result) {
    if (result) {
      f();
    } else {
      setTimeout(function() {
        callFunctionWhenTransactionMined(txHash, f);
      }, 1000);
    }
  });
};

callFunctionWhenTransactionMined($("#txn_hash").attr('value'), function() {
  console.log('here');
  location.reload(1);
});
