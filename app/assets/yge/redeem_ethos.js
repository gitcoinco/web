/* eslint-disable no-console */
window.onload = function() {
  waitforWeb3(function() {
    $('forwarding_address').value = web3.eth.accounts[0];
  });

  setTimeout(function() {
    $('loading').style.display = 'none';
    $('send_eth').style.display = 'block';
  }, 500);
};

function redeemCoin() {
  mixpanel.track('Redeem EthOS Coin Click', {});
  metaMaskWarning();

  var forwarding_address = $('forwarding_address').value;
  var twitter_username = $('twitter_username').value;

  // Check for valid address
  isValidForwardingAddress = forwarding_address.indexOf('0x') != -1;
  if (forwarding_address && !isValidForwardingAddress) {
    _alert({message: gettext('Not a valid forwarding address')}, 'error');
    return;
  }

  // Check for twitter username
  if (!twitter_username) {
    _alert({message: gettext('Please enter your Twitter username')}, 'error');
    return;
  }

  twitter_username = twitter_username.trim();

  var sendEthInnerHTML = $('send_eth').innerHTML;

  $('send_eth').innerHTML = '<img src="/static/yge/images/loading_v2.gif" style="max-width: 70px; max-height: 70px;"><br><h4>Submitting to the blockchain...</h4>';

  fetch(window.location.href, {
    method: 'POST',
    body: JSON.stringify({
      address: forwarding_address ? forwarding_address.trim() : '',
      username: twitter_username
    })
  })
    .then(
      function(response) {
        response.json().then(function(data) {
          if (data.status === 'OK') {
            mixpanel.track('Redeem EthOS Coin Success', {});
            startConfetti();

            $('send_eth').innerHTML = '<h1>Got Ethos?</h1>' +
              '<h3>Prove it -- Give this coin to someone *whom you don\'t know*.</h3>' +
              '<h4>The faster you perform this task, the more Ethos you will receive.</h4>' +
              '<p>This coin has been shared ' + data.num_scans + ' times. ' +
              'The top coin has been shared ' + data.num_scans_top + ' times.</p>' +
              '<a href="' + data.tweet_url + '" target="_blank" rel="noopener noreferrer">Checkout your tweet here</a>';
          } else {
            if (data.message.indexOf('Address has an invalid EIP checksum') !== -1) {
              _alert({message: 'Please enter a valid checksum address.'}, 'warning');
            } else {
              _alert({message: data.message}, 'error');
            }

            $('send_eth').innerHTML = sendEthInnerHTML;

            // Prefill the input fields as the form is attached dynamically to the DOM
            setTimeout(function() {
              document.getElementById('send_eth').querySelector('#forwarding_address').value = forwarding_address;
              document.getElementById('send_eth').querySelector('#twitter_username').value = twitter_username;
            }, 100);

            mixpanel.track('Redeem EthOS Coin Error', {
              error: data.message
            });
          }
        });
      }
    )
    .catch(function(err) {
      console.log('Fetch Error :-S', err);
    });
}
