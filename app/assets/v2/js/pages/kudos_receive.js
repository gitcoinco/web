/* eslint-disable no-console */
var combine_secrets = function(secret1, secret2) {
  var shares = [ secret1, secret2 ];

  return secrets.combine(shares);
};

var sign_and_send = function(rawTx, success_callback, private_key) {
  // sign & serialize raw transaction
  console.log('rawTx: ' + JSON.stringify(rawTx));
  console.log('private_key: ' + private_key);
  var tx = new EthJS.Tx(rawTx);

  var private_key_buffer = new EthJS.Buffer.Buffer.from(private_key, 'hex');
  // console.log(private_key_buffer)

  tx.sign(private_key_buffer);
  var serializedTx = tx.serialize();

  console.log('0x' + serializedTx.toString('hex'));

  // send raw transaction
  web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex')).on('transactionHash', txHash => {
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
    console.log(document.kudos_transfer);
    console.log(document.ipfs_key_to_secret);
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
    if (typeof document.kudos_transfer == 'undefined') {
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

    // redeem kudos

    var gas_price_wei = new web3.utils.BN(parseInt(document.gas_price * 10 ** 9));
    // Not used
    var token_address = document.kudos_transfer['token_address'];
    var kudos_contract = new web3.eth.Contract(kudos_abi, kudos_address());
    var holding_address = document.kudos_transfer['holding_address'];


    web3.eth.getTransactionCount(holding_address, function(error, result) {
      var nonce = result;

      if (!nonce) {
        nonce = 0;
      }
      // find existing holderBalance
      web3.eth.getBalance(holding_address, function(error, result) {
        var holderBalance = new web3.utils.BN(result.toString());

        if (holderBalance == 0) {
          _alert('You must wait until the senders transaction confirm before claiming this Kudos.');
          return;
        }
        var rawTx;

        // Build the raw transaction data for the kudos clone & transfer
        var kudosId = $('#kudosid').data('kudosid');
        var tokenId = $('#tokenid').data('tokenid');
        var numClones = 1;
        var data = kudos_contract.methods.clone(forwarding_address, tokenId, numClones).encodeABI();

        // create the raw transaction
        rawTx = {
          nonce: web3.utils.toHex(nonce),
          to: kudos_address(),
          from: holding_address,
          data: data
        };

        var kudosPriceInEth = parseFloat($('#kudosPrice').attr('data-ethprice'));

        console.log(kudosPriceInEth);
        var kudosPriceInWei = new web3.utils.BN(web3.utils.toWei(String(kudosPriceInEth)));
        var params = {
          forwarding_address: forwarding_address,
          tokenid: tokenId,
          numClones: numClones,
          holding_address: holding_address,
          kudosPriceInWei: kudosPriceInWei.toString(10)
        };

        console.log('params for kudos clone:');
        console.log(params);
        kudos_contract.methods.clone(forwarding_address, tokenId, numClones).estimateGas({
          from: holding_address,
          value: kudosPriceInWei
        }, function(error, gasLimit) {
          if (error) {
            _alert({ message: error.message}, 'danger');
          }

          var buffer = new web3.utils.BN(10);

          var observedKudosGasLimit = 505552;

          if (gasLimit < observedKudosGasLimit) {
            gasLimit = observedKudosGasLimit;
          }

          gasLimit = new web3.utils.BN(gasLimit);
          var send_amount = holderBalance.sub(gasLimit.mul(gas_price_wei)).sub(buffer);

          rawTx['value'] = send_amount.toNumber();
          rawTx['gasPrice'] = web3.utils.toHex(gas_price_wei.toString());
          rawTx['gasLimit'] = web3.utils.toHex(gasLimit.toString());
          show_console = true;
          if (show_console) {
            console.log('from_addr ', holding_address);
            console.log('holderBalance ', holderBalance.toString());
            console.log('sending ', send_amount.toString());
            console.log('gas ', (gasLimit.mul(gas_price_wei)).toString());
            console.log('gas price ', (gas_price_wei.toString()));
            console.log('buffer ', (buffer.toString()));
            console.log('holderBalance > value ', holderBalance > send_amount);
            console.log(rawTx);
          }
          sign_and_send(rawTx, success_callback, document.priv_key);
          //   console.log('txid:' + txid)
          // })
        });
      });
    });
  });
});
