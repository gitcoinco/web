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
  web3.eth.sendRawTransaction('0x' + serializedTx.toString('hex'), success_callback);

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
    if (typeof document.kudos_transfer == 'undefined') {
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

    // redeem kudos

    var gas_price_wei = new web3.BigNumber(parseInt(document.gas_price * 10 ** 9));
    // Not used
    var token_address = document.kudos_transfer['token_address'];
    var kudos_contract = web3.eth.contract(kudos_abi).at(kudos_address());
    var holding_address = document.kudos_transfer['holding_address'];
    

    web3.eth.getTransactionCount(holding_address, function(error, result) {
      var nonce = result;

      if (!nonce) {
        nonce = 0;
      }
      // find existing balance
      web3.eth.getBalance(holding_address, function(error, result) {
        var balance = new web3.BigNumber(result.toString());

        if (balance == 0) {
          _alert('You must wait until the senders transaction confirm before claiming this Kudos.');
          return;
        }
        var rawTx;

        // Build the raw transaction data for the kudos clone & transfer
        var kudosId = $('#kudosid').data('kudosid');
        var tokenId = $('#tokenid').data('tokenid');
        var numClones = 1;
        var data = kudos_contract.clone.getData(forwarding_address, tokenId, numClones);

        // create the raw transaction
        rawTx = {
          nonce: web3.toHex(nonce),
          to: kudos_address(),
          from: holding_address,
          data: data
        };
        // console.log(rawTx)

        var kudosPriceInEth = parseFloat($('#kudosPrice').attr('data-ethprice'));

        console.log(kudosPriceInEth);
        var kudosPriceInWei = new web3.BigNumber(kudosPriceInEth * 1.0 * Math.pow(10, 18));

        var params = {
          forwarding_address: forwarding_address,
          tokenid: tokenId,
          numClones: numClones,
          holding_address: holding_address,
          kudosPriceInWei: kudosPriceInWei.toString(10)
        };

        console.log('params for kudos clone:');
        console.log(params);
 
        kudos_contract.clone.estimateGas(forwarding_address, tokenId, numClones, {from: holding_address, value: kudosPriceInWei}, function(error, gasLimit) {
          console.log(gasLimit);

          var buffer = new web3.BigNumber(10);

          var observedKudosGasLimit = 505552;

          if (gasLimit < observedKudosGasLimit) {
            gasLimit = observedKudosGasLimit;
          }

          gasLimit = new web3.BigNumber(gasLimit);
          var send_amount = balance.minus(gasLimit.times(gas_price_wei)).minus(buffer);

          rawTx['value'] = send_amount.toNumber();
          rawTx['gasPrice'] = web3.toHex(gas_price_wei.toString());
          rawTx['gasLimit'] = web3.toHex(gasLimit.toString());
          show_console = true;
          if (show_console) {
            console.log('from_addr ', holding_address);
            console.log('balance ', balance.toString());
            console.log('sending ', send_amount.toString());
            console.log('gas ', (gasLimit.times(gas_price_wei)).toString());
            console.log('gas price ', (gas_price_wei.toString()));
            console.log('buffer ', (buffer.toString()));
            console.log('balance > value ', balance > send_amount);
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