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
  web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
    .on('transactionHash', txHash => {
      console.log('transactionHash:', txHash);
      success_callback(undefined, txHash);
    })
    .on('receipt', receipt => {
      console.log('receipt:', receipt);
    })
    .on('confirmation', (confirmationNumber, receipt) => {
      if (confirmationNumber >= 1) {
        console.log('confirmations:', confirmationNumber, receipt);
      }
    })
    .on('error:', error => {
      success_callback(error, undefined);
    });
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
        _alert('Could not reach IPFS.  please try again later.', 'danger');
        return;
      }
      document.priv_key = combine_secrets(key2, document.gitcoin_secret);
    });
  });
  waitforWeb3(function() {
    if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'danger');
    } else if (!$('#forwarding_address').val()) {
      web3.eth.getCoinbase(function(_, coinbase) {
        $('#forwarding_address').val(coinbase);
      });
    }
    $('#network').val(document.web3network);
  });
};

$(document).ready(function() {
  $(document).on('click', '#receive', function(e) {
    e.preventDefault();

    if (!provider) {
      return onConnect();
    }

    var forwarding_address = $('#forwarding_address').val();

    if (!$('#tos').is(':checked')) {
      _alert('Please accept TOS.', 'danger');
      unloading_button($(this));
      return;
    }
    if (forwarding_address == '0x0' || forwarding_address == '') {
      _alert('Invalid forwarding address.', 'danger');
      unloading_button($(this));
      return;
    }
    if (typeof web3 == 'undefined') {
      _alert({ message: gettext('You are not on a web3 browser.  Please switch to a web3 browser.') }, 'danger');
      unloading_button($(this));
      return;
    }
    if (typeof document.tip == 'undefined') {
      _alert({ message: gettext('You do not have permission to do that.') }, 'danger');
      return;
    }

    if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'danger');
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
        _alert(err.message.split('\n')[0], 'danger');
      } else {
        const url = window.location.href.split('?')[0];
        const csrfmiddlewaretoken = $('[name=csrfmiddlewaretoken]').val();
        const forwardingAddress = $('#forwarding_address').val();
        const saveAddr = ($('#save_addr').is(':checked') ? '1' : '0');
        const form = $(`
          <form action="${url}" method="post" class="d-none">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfmiddlewaretoken}">
            <input type="text" name="receive_txid" value="${txid}">
            <input type="text" name="forwarding_address" value="${forwardingAddress}">
            <input type="text" name="save_addr" value="${saveAddr}">
          </form>`);

        $('body').append(form);
        form.submit();
      }
    };

    // redeem tip


    document.tip['token_address'] = document.tip['token_address'] == '0x0' ? '0x0000000000000000000000000000000000000000' : document.tip['token_address'];
    var gas_price_wei = new web3.utils.BN(document.gas_price * 10 ** 9);
    var is_eth = document.tip['token_address'] == '0x0' || document.tip['token_address'] == '0x0000000000000000000000000000000000000000';
    var token_address = document.tip['token_address'];
    var token_contract = new web3.eth.Contract(token_abi, token_address);
    var holding_address = document.tip['holding_address'];
    var amount_in_wei = new web3.utils.BN(String(document.tip['amount_in_wei']));

    web3.eth.getTransactionCount(holding_address, function(error, result) {
      var nonce = result;

      if (!nonce) {
        nonce = 0;
      }
      // find existing balance
      web3.eth.getBalance(holding_address, function(error, result) {
        var holderBalance = new web3.utils.BN(result.toString());

        if (holderBalance == 0) {
          _alert('You must wait until the senders transaction confirm before claiming this tip.');
          return;
        }
        var rawTx;

        if (is_eth) {
          // send ETH
          rawTx = {
            nonce: web3.utils.toHex(nonce),
            to: forwarding_address,
            from: holding_address,
            value: amount_in_wei.toString()
          };
          web3.eth.estimateGas(rawTx, function(err, gasLimit) {
            var buffer = new web3.utils.BN(0);

            gasLimit = new web3.utils.BN(gasLimit);
            var send_amount = holderBalance.sub(gasLimit.mul(gas_price_wei)).sub(buffer);

            if (document.override_send_amount && (document.override_send_amount * 10 ** 18) < send_amount) {
              send_amount = document.override_send_amount * 10 ** 18; // TODO: decimals
            }

            rawTx['value'] = web3.utils.toHex(send_amount.toString()); // deduct gas costs from amount to send
            rawTx['gasPrice'] = web3.utils.toHex(gas_price_wei.toString());
            rawTx['gas'] = web3.utils.toHex(gasLimit.toString());
            rawTx['gasLimit'] = web3.utils.toHex(gasLimit.toString());
            show_console = false;
            if (show_console) {
              console.log('addr ', holding_address);
              console.log('holderBalance ', holderBalance.toString());
              console.log('sending ', send_amount.toString());
              console.log('gas ', (gasLimit.mul(gas_price_wei)).toString());
              console.log('gas price ', (gas_price_wei.toString()));
              console.log('buffer ', (buffer.toString()));
              console.log('holderBalance > value ', holderBalance > send_amount);
              console.log(rawTx);
            }
            sign_and_send(rawTx, success_callback, document.priv_key);
          });
        } else {

          // send ERC20
          var encoded_amount = new web3.utils.BN(BigInt(document.tip['amount_in_wei'])).toString();
          var data = token_contract.methods.transfer(forwarding_address, encoded_amount).encodeABI();

          rawTx = {
            nonce: web3.utils.toHex(nonce),
            to: token_address,
            from: holding_address,
            value: '0x00',
            data: data
          };

          web3.eth.estimateGas(rawTx, function(err, gasLimit) {
            rawTx['gasPrice'] = web3.utils.toHex(gas_price_wei.toString());
            rawTx['gas'] = web3.utils.toHex(gasLimit.toString());
            rawTx['gasLimit'] = web3.utils.toHex(gasLimit.toString());
            var will_fail_at_this_gas_price = (gas_price_wei * gasLimit) > holderBalance;

            if (will_fail_at_this_gas_price) { // adjust if gas prices have increased since this tx was created
              rawTx['gasPrice'] = Math.floor(holderBalance / gasLimit / 10 ** 9);
            }
            sign_and_send(rawTx, success_callback, document.priv_key);
          });
        }
      });
    });
  });
});
