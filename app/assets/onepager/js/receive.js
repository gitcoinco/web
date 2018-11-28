/* eslint-disable no-console */
var combine_secrets = function(secret1, secret2) {
  var shares = [ secret1, secret2 ];

  return secrets.combine(shares);
};

var sign_and_send = function(rawTx, success_callback, private_key) {
  // sign & serialize raw transaction
  var tx = new EthJS.Tx(rawTx);

  tx.sign(new EthJS.Buffer.Buffer.from(private_key, 'hex'));
  var serializedTx = tx.serialize();

  // send raw transaction
  web3.eth.sendRawTransaction('0x' + serializedTx.toString('hex'), success_callback);
};

window.onload = function() {
  waitforWeb3(function() {
    ipfs.ipfsApi = IpfsApi(ipfsConfig);
    ipfs.setProvider(ipfsConfig);
    if (typeof document.ipfs_key_to_secret == 'undefined') {
      return;
    }
    ipfs.catText(document.ipfs_key_to_secret, function(err, key2) {
      if (err) {
        _alert('Could not reach IPFS.  please try again later.', 'error');
        return;
      }
      document.priv_key = combine_secrets(key2, document.gitcoin_secret);
    });
  });
  waitforWeb3(function() {
    if (document.web3network != document.network) {
      if (document.web3network == 'locked') {
        _alert({ message: gettext('Please authorize Metamask in order to continue.')}, 'info');
        approve_metamask();
      } else {
        _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
      }

    } else if (!$('#forwarding_address').val()) {
      $('#forwarding_address').val(web3.eth.coinbase);
    }
    $('#network').val(document.web3network);
  });
};

$(document).ready(function() {
  $(document).on('click', '#receive', function(e) {
    e.preventDefault();

    var forwarding_address = $('#forwarding_address').val();

    if (!$('#tos').is(':checked')) {
      _alert('Please accept TOS.', 'error');
      unloading_button($(this));
      return;
    }
    if (forwarding_address == '0x0' || forwarding_address == '') {
      _alert('Invalid forwarding address.', 'error');
      unloading_button($(this));
      return;
    }
    if (typeof web3 == 'undefined') {
      _alert({ message: gettext('You are not on a web3 browser.  Please switch to a web3 browser.') }, 'error');
      unloading_button($(this));
      return;
    }
    if (typeof document.tip == 'undefined') {
      _alert({ message: gettext('You do not have permission to do that.') }, 'error');
      return;
    }

    if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
      unloading_button($(this));
      return;
    }

    if (!confirm(gettext('Please confirm that ' + forwarding_address + ' is the address for which you wish to redeem this tip.'))) {
      unloading_button($(this));
      return;
    }

    loading_button($(this));

    var success_callback = function(err, txid) {
      unloading_button($(this));
      if (err) {
        _alert(err.message.split('\n')[0], 'error');
      } else {
        document.location.href = window.location.href.split('?')[0] +
        '?receive_txid=' + txid +
        '&forwarding_address=' + $('#forwarding_address').val() +
        '&save_addr=' + ($('#save_addr').is(':checked') ? '1' : '0');
      }
    };

    // redeem tip

    var gas_price_wei = new BigNumber(document.gas_price * 10 ** 9);
    var is_eth = document.tip['token_address'] == '0x0' || document.tip['token_address'] == '0x0000000000000000000000000000000000000000';
    var token_address = document.tip['token_address'];
    var token_contract = web3.eth.contract(token_abi).at(token_address);
    var holding_address = document.tip['holding_address'];
    var amount_in_wei = new BigNumber(document.tip['amount_in_wei']);

    web3.eth.getTransactionCount(holding_address, function(error, result) {
      var nonce = result;

      if (!nonce) {
        nonce = 0;
      }
      // find existing balance
      web3.eth.getBalance(holding_address, function(error, result) {
        var balance = new BigNumber(result.toString());

        if (balance == 0) {
          _alert('You must wait until the senders transaction confirm before claiming this tip.');
          return;
        }
        var rawTx;

        if (is_eth) {
          // send ETH
          rawTx = {
            nonce: web3.toHex(nonce),
            to: forwarding_address,
            from: holding_address,
            value: amount_in_wei.toString()
          };
          web3.eth.estimateGas(rawTx, function(err, gasLimit) {
            var buffer = new BigNumber(0);

            gasLimit = new BigNumber(gasLimit);
            var send_amount = balance.minus(gasLimit.times(gas_price_wei)).minus(buffer);

            rawTx['value'] = web3.toHex(send_amount.toString()); // deduct gas costs from amount to send
            rawTx['gasPrice'] = web3.toHex(gas_price_wei.toString());
            rawTx['gas'] = web3.toHex(gasLimit.toString());
            rawTx['gasLimit'] = web3.toHex(gasLimit.toString());
            show_console = false;
            if (show_console) {
              console.log('addr ', holding_address);
              console.log('balance ', balance.toString());
              console.log('sending ', send_amount.toString());
              console.log('gas ', (gasLimit.times(gas_price_wei)).toString());
              console.log('gas price ', (gas_price_wei.toString()));
              console.log('buffer ', (buffer.toString()));
              console.log('balance > value ', balance > send_amount);
              console.log(rawTx);
            }
            sign_and_send(rawTx, success_callback, document.priv_key);
          });
        } else {

          // send ERC20
          var data = token_contract.transfer.getData(forwarding_address, amount_in_wei.toString());

          rawTx = {
            nonce: web3.toHex(nonce),
            to: token_address,
            from: holding_address,
            value: '0x00',
            data: data
          };

          web3.eth.estimateGas(rawTx, function(err, gasLimit) {
            rawTx['gasPrice'] = gas_price_wei.toNumber();
            rawTx['gas'] = gasLimit;
            rawTx['gasLimit'] = gasLimit;
            var will_fail_at_this_gas_price = (gas_price_wei * gasLimit) > balance;

            if (will_fail_at_this_gas_price) { // adjust if gas prices have increased since this tx was created
              rawTx['gasPrice'] = Math.floor(balance / gasLimit / 10 ** 9);
            }
            sign_and_send(rawTx, success_callback, document.priv_key);
          });
        }
      });
    });
  });
});