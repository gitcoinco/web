/* eslint-disable no-console */
window.onload = function() {
  setTimeout(function() {
    $('loading').style.display = 'none';
    $('send_eth').style.display = 'block';
  }, 500);
};

function redeemCoin() {
  mixpanel.track('Redeem Coin Click', {});
  metaMaskWarning();

  var forwarding_address = $('forwarding_address').value;
  var twitter_username = $('twitter_username').value;

  // Check for valid address
  isValidForwardingAddress = forwarding_address.indexOf('0x') != -1;
  if (!forwarding_address || !isValidForwardingAddress) {
    _alert({message: gettext('Not a valid forwarding address')}, 'error');
    return;
  }

  // Check for twitter username
  if (!twitter_username) {
    _alert({message: gettext('Please enter your Twitter username')}, 'error');
    return;
  }

  var sendEthInnerHTML = $('send_eth').innerHTML;

  $('send_eth').innerHTML = '<img src="/static/yge/images/loading_v2.gif" style="max-width: 70px; max-height: 70px;"><br><h4>Submitting to the blockchain...</h4>';

  fetch(window.location.href, {
    method: 'POST',
    body: JSON.stringify({
      address: forwarding_address.trim(),
      username: twitter_username.trim()
    })
  })
    .then(
      function(response) {
        response.json().then(function(data) {
          if (data.status === 'OK') {
            mixpanel.track('Redeem EthOS Coin Success', {});
            startConfetti();
            $('send_eth').innerHTML = '<h1>Success 🚀!</h1> <a href="https://' + etherscanDomain() + '/tx/' + data.message + '" target="_blank" rel="noopener noreferrer">See your transaction on the blockchain here</a>.<br><br><span id="mighttake">It might take a few minutes to sync, depending upon: <br> - network congestion<br> - network fees that sender allocated to transaction<br></span><br><a href="/" class="button">⬅ Check out Gitcoin.co</a>';
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
