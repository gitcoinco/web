/* eslint-disable no-console */
window.onload = function() {

  setTimeout(function() {
    var txid;

    if (!web3.currentProvider || !web3.currentProvider.isMetaMask) {
      $('step_zero').style.display = 'block';
      $('send_eth').style.display = 'none';
      $('loading').style.display = 'none';
    } else {
      txid = getParam('txid');
      var link = 'https://' + etherscanDomain() + '/tx/' + txid;

      $('loading_txt').innerHTML = 'Waiting for <a href="' + link + '" target="_blank" rel="noopener noreferrer">transaction</a> to be mined..<br><br><a href="#" title="If the transaction seems to be loading forever, you can skip this step." style="border: 1px solid #fc7596; padding 5px 10px;" onclick="document.receive_tip_callback ()">Skip Wait</a>';
    }

    document.receive_tip_callback = function() {
      $('loading').style.display = 'none';
      if (web3.currentProvider.isMetaMask) {
        $('send_eth').style.display = 'block';
        $('step_zero').style.display = 'none';

        var private_key = $('private_key').value;
        var address = '0x' + lightwallet.keystore._computeAddressFromPrivKey(private_key);

        contract().getTransferDetails.call(address, function(errors, result) {
          if (errors) {
            $('step_zero').style.display = 'block';
            $('send_eth').style.display = 'none';
            mixpanel.track('Tip Receive Error', {step: 'transferdetails', error: errors});
          } else {
            var active = result[0];

            if (!active) {
              $('send_eth').innerHTML = 'Need help?  Try asking <a href="/slack">on slack</a>.';
              $('step_zero').style.display = 'none';
              console.error('tip_inactive', result);
              var error = 'This tip is no longer active  Please contact the sender or reach out for help on the Gitcoin slack.';

              _alert({message: error}, 'error');
              mixpanel.track('Tip Receive Error', {step: 'transferdetails2', error: error});
              return;
            }
            var amount = result[1].toNumber();
            var developer_tip_pct = result[2].toNumber();
            var initialized = result[3];
            var expiration_time = result[4].toNumber();
            var from = result[5];
            var owner = result[6];
            var erc20contract = result[7];
            var token = 'ETH';
            var tokenDetails = tokenAddressToDetails(erc20contract);
            var decimals = 18;

            if (tokenDetails) {
              token = tokenDetails.name;
              decimals = tokenDetails.decimals;
            }
            var round_to = Math.pow(10, 5);

            amount = Math.round(round_to * amount / Math.pow(10, decimals)) / round_to;
            var _text = 'You\'ve Received ' + amount + ' ' + getWarning() + ' ' + token + '!';

            $('zeroh1').innerHTML = _text;
            $('oneh1').innerHTML = _text;
            $('tokenName').innerHTML = token;
            $('send_eth').style.display = 'block';

          }
        });

      }
    };
    callFunctionWhenTransactionMined(txid, document.receive_tip_callback);
  }, 500);


  if (!getParam('key')) {
    $('send_eth').innerHTML = '<h1>Error 🤖</h1> Invalid Link.  Please check your link and try again';
    return;
  }

  // default form values
  $('private_key').value = getParam('key');

  // When 'Generate Account' is clicked
  $('receive').onclick = function() {
    mixpanel.track('Tip Receive Click', {});
    metaMaskWarning();

    // get form data
    var private_key = $('private_key').value;
    var _idx = '0x' + lightwallet.keystore._computeAddressFromPrivKey(private_key);

    console.log('fromAccount: ' + _idx);
    var forwarding_address = $('forwarding_address').value.trim();

    if (!forwarding_address || forwarding_address == '0x0') {
      _alert({message: 'Not a valid forwarding address.'}, 'warning');
      return;
    }

    if (!_idx || _idx == '0x0') {
      _alert({message: 'Invalid Link.  Please check your link and try again'}, 'warning');
      return;
    }
    if (!private_key) {
      _alert({message: 'Invalid Link.  Please check your link and try again'}, 'warning');
      return;
    }
    $('send_eth').innerHTML = "<img src='/static/yge/images/loading_v2.gif' style='max-width: 70px; max-height: 70px;'><br><h4>Submitting to the blockchain..</h4>";
    loading_button(jQuery('#receive'));
    // set up callback to sendRawTransaction
    var callback = function(error, result) {
      if (error) {
        console.log(error);
        _alert({message: 'got an error :('}, 'error');
        mixpanel.track('Tip Receive Error', {step: 'callback', error: error});
        unloading_button(jQuery('#receive'));
      } else {
        startConfetti();
        mixpanel.track('Tip Receive Success', {});
        $('send_eth').innerHTML = '<h1>Success 🚀!</h1> <a href="https://' + etherscanDomain() + '/tx/' + result + '">See your transaction on the blockchain here</a>.<br><br><strong>Status:</strong> <span id="status">Confirming Transaction … <br><img src="/static/yge/images/loading_v2.gif" style="max-width: 30px; max-height: 30px;"></span><br><br><span id="mighttake">It might take a few minutes to sync, depending upon: <br> - network congestion<br> - network fees that sender allocated to transaction.<br>You may close this browser window.<br></span><br><a href="/" class="button">⬅ Back to Gitcoin.co</a>';
        const url = '/tip/receive';

        fetch(url, {
          method: 'POST',
          body: JSON.stringify({
            txid: getParam('txid'),
            receive_txid: result,
            receive_address: forwarding_address
          })
        });
        callFunctionWhenTransactionMined(result, function() {
          $('status').innerHTML = 'Confirmed ⚡️';
          $('mighttake').innerHTML = '';
        });
      }
    };

        // find the nonce
    web3.eth.getTransactionCount(_idx, function(error, result) {
      var nonce = result;

      if (!nonce) {
        nonce = 0;
      }
      web3.eth.getBalance(_idx, function(error, result) {
        var balance = result.toNumber();

        if (balance == 0) {
          _alert({message: 'You must wait until the senders transaction confirms.'}, 'warning');
          return;
        }

        // setup raw transaction
        var estimate = Math.pow(10, 5);
        var gasPrice = Math.pow(10, 9) * 1.7;

        if (getParam('gasPrice')) {
          gasPrice = Math.pow(10, 9) * getParam('gasPrice');
        }
        var data = contract().claimTransfer.getData(_idx, forwarding_address);
        var payloadData = data; // ??
        var fromAccount = _idx; // ???
        var gas = estimate;
        // maximize the gas price

        if (balance > (gas * gasPrice)) {
          gasPrice = balance / (gas + 1);
        }
        gasPrice = parseInt(gasPrice);
        console.log('balance: ' + balance + ' wei ');
        console.log('balance: ' + (balance / Math.pow(10, 18)) + ' eth ');
        console.log('gas: ' + gas);
        console.log('gasPrice: ' + gasPrice);
        console.log('delta (needed - actual): ' + (balance - (gas * gasPrice)) + ' wei');
        console.log('delta (needed - actual): ' + ((balance - (gas * gasPrice))) / Math.pow(10, 18) + ' eth');
        var gasLimit = gas + 1;
        var rawTx = {
          nonce: web3.toHex(nonce),
          gasPrice: web3.toHex(gasPrice),
          gasLimit: web3.toHex(gasLimit),
          gas: web3.toHex(gas),
          to: contract_address(),
          from: fromAccount,
          value: '0x00',
          data: payloadData
        };

        // sign & serialize raw transaction
        var tx = new EthJS.Tx(rawTx);

        tx.sign(new EthJS.Buffer.Buffer.from(private_key, 'hex'));
        var serializedTx = tx.serialize();

        // send raw transaction
        web3.eth.sendRawTransaction('0x' + serializedTx.toString('hex'), callback);

      });
    });
  };
};
