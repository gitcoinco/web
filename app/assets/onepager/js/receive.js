/* eslint-disable no-console */
var combine_secrets = function(secret1, secret2) {
  var shares = [ secret1, secret2 ];

  return secrets.combine(shares);
};

window.onload = function() {
  waitForWeb3(function() {
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
  waitForWeb3(function() {
    if (document.web3network != document.network) {
      if (document.web3network == 'locked') {
        _alert({ message: gettext('Please authorize Metamask in order to continue.')}, 'info');
        approveMetamask();
      } else {
        _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
      }

    } else if (!$('#forwarding_address').val()) {
      $('#forwarding_address').val(document.coinbase);
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

    var gas_price_wei = window.web3.utils.toBN(document.gas_price * 10 ** 9);
    var is_eth = document.tip['token_address'] == '0x0' || document.tip['token_address'] == '0x0000000000000000000000000000000000000000';
    var token_address = document.tip['token_address'];
    var holding_address = document.tip['holding_address'];
    var amount_in_wei = window.web3.utils.toBN(document.tip['amount_in_wei']);

    window.web3.eth.getTransactionCount(holding_address).then(
      function(result) {
        var nonce = result;

        if (!nonce) {
          nonce = 0;
        }
        // find existing balance
        window.web3.eth.getBalance(holding_address).then(
          function(result) {
            var balance = window.web3.utils.toBN(result);

            if (balance == 0) {
              _alert('You must wait until the senders transaction confirm before claiming this tip.');
              return;
            }
            var rawTx;

            if (is_eth) {
              // send ETH
              rawTx = {
                nonce: window.web3.utils.toHex(nonce),
                to: forwarding_address,
                from: holding_address,
                value: amount_in_wei.toString()
              };
              window.web3.eth.estimateGas(rawTx).then(
                function(gasLimit) {
                  gasLimit = window.web3.utils.toBN(gasLimit);

                  var buffer = window.web3.utils.toBN(0);
                  var send_amount = balance.sub(gasLimit.mul(gas_price_wei)).sub(buffer);

                  rawTx['value'] = window.web3.utils.toHex(send_amount.toString()); // deduct gas costs from amount to send
                  rawTx['gasPrice'] = window.web3.utils.toHex(gas_price_wei.toString());
                  rawTx['gas'] = window.web3.utils.toHex(gasLimit.toString());
                  rawTx['gasLimit'] = rawTx['gas'];
                  show_console = false;
                  if (show_console) {
                    console.log('addr ', holding_address);
                    console.log('balance ', balance.toString());
                    console.log('sending ', send_amount.toString());
                    console.log('gas ', (gasLimit.mul(gas_price_wei)).toString());
                    console.log('gas price ', (gas_price_wei.toString()));
                    console.log('buffer ', (buffer.toString()));
                    console.log('balance > value ', balance > send_amount);
                    console.log(rawTx);
                  }
                  sign_and_send(rawTx, success_callback, document.priv_key);
                });
            } else {

              // send ERC20
              const token_contract = new window.web3.eth.Contract(token_abi, token_address);
              const data = token_contract.methods.transfer(forwarding_address, amount_in_wei.toString()).encodeABI();

              rawTx = {
                nonce: window.web3.utils.toHex(nonce),
                to: token_address,
                from: holding_address,
                value: '0x00',
                data: data
              };

              window.web3.eth.estimateGas(rawTx).then(
                function(gasLimit) {
                  gasLimit = window.web3.utils.toBN(gasLimit);

                  rawTx['gasPrice'] = window.web3.utils.toHex(gas_price_wei.toString());
                  rawTx['gas'] = window.web3.utils.toHex(gasLimit.toString());
                  rawTx['gasLimit'] = rawTx['gas'];
                  var will_fail_at_this_gas_price = (gas_price_wei.mul(gasLimit)) > balance;

                  if (will_fail_at_this_gas_price) { // adjust if gas prices have increased since this tx was created
                    rawTx['gasPrice'] = window.web3.utils.toHex(balance.div(gasLimit));
                  }
                  sign_and_send(rawTx, success_callback, document.priv_key);
                }
              );
            }
          });
      });
  });
});
