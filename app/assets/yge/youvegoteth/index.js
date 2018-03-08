/* eslint-disable nonblock-statement-body-position */
var abi = [{'inputs': [{'type': 'address', 'name': '_idx'}, {'type': 'address', 'name': '_to'}], 'constant': false, 'name': 'claimTransfer', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': ''}], 'constant': true, 'name': 'transfers', 'outputs': [{'type': 'bool', 'name': 'active'}, {'type': 'uint256', 'name': 'amount'}, {'type': 'uint256', 'name': 'developer_tip_pct'}, {'type': 'bool', 'name': 'initialized'}, {'type': 'uint256', 'name': 'expiration_time'}, {'type': 'address', 'name': 'from'}, {'type': 'address', 'name': 'owner'}, {'type': 'address', 'name': 'erc20contract'}, {'type': 'uint256', 'name': 'fee_amount'}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'bool', 'name': '_disableDeveloperTip'}, {'type': 'address', 'name': '_owner'}, {'type': 'address', 'name': '_contract'}, {'type': 'uint256', 'name': '_amount'}, {'type': 'uint256', 'name': '_fee_amount'}, {'type': 'uint256', 'name': 'expires'}], 'constant': false, 'name': 'newTransfer', 'outputs': [], 'payable': true, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_idx'}], 'constant': false, 'name': 'getTransferDetails', 'outputs': [{'type': 'bool', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'bool', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'address', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_idx'}], 'constant': false, 'name': 'expireTransfer', 'outputs': [], 'payable': false, 'type': 'function'}, {'inputs': [], 'type': 'constructor', 'payable': false}, {'payable': true, 'type': 'fallback'}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'uint256', 'name': 'amount'}, {'indexed': false, 'type': 'address', 'name': 'erc20contract'}, {'indexed': false, 'type': 'address', 'name': 'index'}], 'type': 'event', 'name': 'transferSubmitted', 'anonymous': false}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'uint256', 'name': 'amount'}, {'indexed': false, 'type': 'address', 'name': 'erc20contract'}, {'indexed': false, 'type': 'address', 'name': 'index'}], 'type': 'event', 'name': 'transferExpired', 'anonymous': false}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_to'}, {'indexed': false, 'type': 'uint256', 'name': 'amount'}, {'indexed': false, 'type': 'address', 'name': 'erc20contract'}, {'indexed': false, 'type': 'address', 'name': 'index'}], 'type': 'event', 'name': 'transferClaimed', 'anonymous': false}];
var tokenabi = [{'inputs': [{'type': 'address', 'name': '_spender'}, {'type': 'uint256', 'name': '_value'}], 'constant': false, 'name': 'approve', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'totalSupply', 'outputs': [{'type': 'uint256', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_from'}, {'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_value'}], 'constant': false, 'name': 'transferFrom', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_owner'}], 'constant': true, 'name': 'balanceOf', 'outputs': [{'type': 'uint256', 'name': 'balance'}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_value'}], 'constant': false, 'name': 'transfer', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_owner'}, {'type': 'address', 'name': '_spender'}], 'constant': true, 'name': 'allowance', 'outputs': [{'type': 'uint256', 'name': 'remaining'}], 'payable': false, 'type': 'function'}, {'inputs': [{'indexed': true, 'type': 'address', 'name': 'owner'}, {'indexed': true, 'type': 'address', 'name': 'spender'}, {'indexed': false, 'type': 'uint256', 'name': 'value'}], 'type': 'event', 'name': 'Approval', 'anonymous': false}, {'inputs': [{'indexed': true, 'type': 'address', 'name': 'from'}, {'indexed': true, 'type': 'address', 'name': 'to'}, {'indexed': false, 'type': 'uint256', 'name': 'value'}], 'type': 'event', 'name': 'Transfer', 'anonymous': false}];

var getWarning = function() {
  var warning = '';

  if (document.web3network == 'ropsten') {
    warning = '(Ropsten)';
  } else if (document.web3network == 'custom network') {
    warning = '(TestRPC)';
  }
  return warning;
};

function getParam(parameterName) {
  var result = null;
  var tmp = [];

  location.search
    .substr(1)
    .split('&')
    .forEach(function(item) {
      tmp = item.split('=');
      if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
    });
  return result;
}

// figure out what network to point at
// default to latest contract, unless user has a link to receive.html where addres/key are specificed but contract verseion is not.
var contract_address = function() {
  var contract_address;

  if (document.web3network == 'custom network') {
    // testrpc
    contract_address = '0x852624f8b99431a354bf11543b10762fd3cdfae3';
  } else if (document.web3network == 'ropsten') {
    // ropsten
    contract_address = '0xb917e0f1fdebb89d37cbe053f59066a20b6794d6'; // ropsten v1
  } else {
    // mainnet
    contract_address = '0x5479b8be3b8e9459616721f8b588df593c6e4178'; // mainnet v1
  }
  return contract_address;
};
var etherscanDomain = function() {
  var etherscanDomain = 'etherscan.io';

  if (document.web3network == 'custom network') {
    // testrpc
    etherscanDomain = 'localhost';
  } else if (document.web3network == 'ropsten') {
    // ropsten
    etherscanDomain = 'ropsten.etherscan.io';
  } else {
    // mainnet
  }
  return etherscanDomain;
};
var contract = function() {
  return web3.eth.contract(abi).at(contract_address());
};
var token_contract = function(token_address) {
  return web3.eth.contract(tokenabi).at(token_address);
};

// background moving
var addMotion = function() {
  if (!$('yge')) {
    return setTimeout(addMotion, 50);
  }
  var startX = null;
  var startY = null;
  var movementStrength = 25;
  var _height = 1000;
  var _width = 1000;
  var height = movementStrength / _height;
  var width = movementStrength / _width;

  if (typeof $('yge').addEventListener != 'undefined') {
    $('yge').addEventListener('mousemove', function(e) {
      var pageX = e.pageX - (_height / 2);
      var pageY = e.pageY - (_width / 2);
      var newvalueX = width * (pageX - startX) * -1 - 25;
      var newvalueY = height * (pageY - startY) * -1 - 50;

      if (!startX) {
        startX = newvalueX;
      }
      if (!startY) {
        startY = newvalueY;
      }
      $('yge').style.backgroundPosition = (newvalueX - startX - 10) + 'px     ' + (newvalueY - startY - 10) + 'px';
    });
  }
};

setTimeout(addMotion, 5);

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

var loading_button = function(button) {
  button.prepend('<img src=/static/v2/images/loading_v2.gif style="max-width:10px; max-height: 10px; margin-right: 5px">').addClass('disabled');
};

var unloading_button = function(button) {
  button.removeClass('disabled');
  button.find('img').remove();
};

setTimeout(function() {
  var web3v = (typeof web3 == 'undefined' || typeof web3.version == 'undefined') ? 'none' : web3.version.api;
  var params = {
    page: document.location.pathname,
    web3: web3v
  };

  if (mixpanel) {
    mixpanel.track('Pageview', params);

  }
}, 300);

