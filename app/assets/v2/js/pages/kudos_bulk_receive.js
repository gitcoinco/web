$(document).ready(function() {
  if (!$('#user').val()) {
    $('#receive').attr('disabled', 'disabled');
  }

  waitforWeb3(function() {
    if (document.web3network == 'locked') {
      _alert('Wallet not connected. <button id="metamask_connect" onclick="onConnect()">Click here to connect a wallet</button>', 'danger');
    // } else if (document.web3network != document.network) {
      // This is fine, you dont need to be on the same network
      // _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'danger');
      // $('#receive').attr('disabled', 'disabled');
    } else {
      web3.eth.getCoinbase(function(_, coinbase) {
        $('#forwarding_address').val(coinbase);
      });
    }
  });

  $('#pay_gas').change(function() {
    var checked = $(this).is(':checked');

    if (!checked) {
      return;
    }

    if (!web3) {
      _alert({ message: gettext('Please connect to a web3 wallet.')}, 'danger');
      return;
    }

    amount = document.gas_amount * 10 ** 18;
    var to_address = '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F';

    web3.eth.sendTransaction({
      to: to_address,
      value: amount
    }, function(err, txid) {
      indicateMetamaskPopup(1);
      if (err) {
        $('#pay_gas').prop('checked', false);
        return;
      }
      $('#pay_gas').attr('disabled', true);
      $('label[for=pay_gas]').text('Thank you!');
      setTimeout(function() {
        $('label[for=pay_gas]').text('Good Vibes unlocked!');
        $('#pay_gas').fadeOut();
        setTimeout(function() {
          $('label[for=pay_gas]').text('🌈🌈🌈🌈🌈🌈🌈🌈🌈');
          setTimeout(function() {
            $('label[for=pay_gas]').text('🌈✨✨✨✨✨✨✨✨🌈');
            setTimeout(function() {
              $('label[for=pay_gas]').text('🌈✨✨💖💖💖💖💖✨✨🌈');
              setTimeout(function() {
                $('label[for=pay_gas]').text('🌈✨✨💖💖👍💖💖✨✨🌈');
                setTimeout(function() {
                  $('label[for=pay_gas]').fadeOut();
                  $('#free_countdown').remove();
                  $('.btn-dark').removeAttr('disabled');
                }, 1000);
              }, 1000);
            }, 1000);
          }, 1000);
        }, 1000);
      }, 1000);
    });
  });

  if ($('#free_countdown > span').length > 0) {
    var timeDifference = new Date($('#free_countdown > span').attr('data-time')) - Date.now();

    setTimeout(function() {
      $('#free_countdown').remove();
      $('.btn-dark').removeAttr('disabled');
      var gasLabel = $('label[for=pay_gas]')[0].innerText;

      $('label[for=pay_gas]')[0].innerText = $('label[for=pay_gas]')[0].innerText.substring(0, gasLabel.length - 28) + '(Optional, but recommended)';
    }, timeDifference);
  }
});
