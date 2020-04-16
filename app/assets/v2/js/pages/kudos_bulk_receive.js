$(document).ready(function() {
  if (!$('#user').val()) {
    $('#receive').attr('disabled', 'disabled');
  }

  waitforWeb3(function() {
    if (document.web3network == 'locked') {
      _alert('Metamask not connected. <button id="metamask_connect" onclick="approve_metamask()">Click here to connect to metamask</button>', 'error');
    } else if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
      $('#receive').attr('disabled', 'disabled');
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
    amount = 0.005 * 10 ** 18;
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
                }, 1000);
              }, 1000);
            }, 1000);
          }, 1000);
        }, 1000);
      }, 1000);
    });
  });

});