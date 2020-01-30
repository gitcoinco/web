$(document).ready(function() {

  // gets multi part (ex: 10 hours 2 minutes 5 seconds) time
  var time_difference_broken_down = function(difference) {
    let remaining = ' now.. Refresh to view offer!';
    let prefix = ' in ';

    if (difference > 0) {
      const parts = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60)
      };

      remaining = Object.keys(parts)
        .map(part => {
          if (!parts[part])
            return;
          return `${parts[part]} ${part}`;
        })
        .join(' ');
    } else {
      return remaining;
    }
    return prefix + remaining;
  };

  // effects when an offer is clicked upon
  $('.offer a').click(function(e) {
    var speed = 500;

    $(this).addClass('clicked');
    $(this).find('#ribbon').effect('puff', speed, function() {
      $(this).find('#giftbox').effect('puff', speed);
    });
  });

  var get_redir_location = function(tab) {
    let trending = $('#trending').is(':checked') ? 1 : 0;

    return '/?tab=' + tab + '&trending=' + trending;
  };

  $('body').on('focus change paste keyup blur', '#keyword', function(e) {
    if ((e.keyCode == 13)) {
      e.preventDefault();
      document.location.href = get_redir_location('search-' + $('#keyword').val());
    }
  });

  $('body').on('click', '#trending', function(e) {
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
  });
  $('body').on('click', '.container .nav-link', function(e) {
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    e.preventDefault();
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
  });

  // updates expiry timers with countdowns
  var updateTimers = function() {
    $('.timer').each(function() {
      var time = $(this).data('time');
      var base_time = $(this).data('base_time');
      var counter = $(this).data('counter');

      if (!counter) {
        counter = 0;
      }
      counter += 1;
      $(this).data('counter', counter);
      var start_date = new Date(new Date(time).getTime() - (1000 * counter));
      var countdown = start_date - new Date(base_time);

      $(this).html(time_difference_broken_down(countdown));
    });
  };

  setInterval(updateTimers, 1000);

  $("#givepenny").on('click', function(e){
      if (!document.contxt.github_handle) {
        _alert('Please login first.', 'error');
        return;
      }
      if (!web3) {
        _alert('Please enable and unlock your web3 wallet.', 'error');
        return;
      }

      const email = '';
      const github_url = $('#issueURL').text();
      const from_name = document.contxt['github_handle'];
      const username = '';
      const amountInEth = parseFloat(prompt("How much ETH do you want to give?", "0.01").replace('ETH',''));
      if (amountInEth < 0.01) {
        _alert('Amount must be 0.01 or more.', 'error');
        return;
      }
      const comments_priv = '';
      const comments_public = "Take a penny; leave a penny jar"
      const accept_tos = (confirm("Do you accept Gitcoin's terms of service at gitcoin.co/terms ?"));
      const from_email = '';
      const tokenAddress = '0x0';
      const expires = 9999999999;

      var success_callback = function(txid) {
        const url = 'https://' + etherscanDomain() + '/tx/' + txid;
        const msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        _alert(msg, 'info', 1000);
        location.reload();
      };

      var failure_callback = function() {
        $.noop(); // do nothing
      };

      return sendTip(
        email,
        github_url,
        from_name,
        username,
        amountInEth,
        comments_public,
        comments_priv,
        from_email,
        accept_tos,
        tokenAddress,
        expires,
        success_callback,
        failure_callback,
        false
      );
  });

  // toggles the daily email sender
  $('#receive_daily_offers_in_inbox').on('change', function(e) {
    _alert('Your email subscription preferences have been updated', 'success', 2000);

    var url = '/api/v0.1/emailsettings/';
    var params = {
      'new_bounty_notifications': $(this).is(':checked'),
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };

    $.post(url, params, function(response) {
      // no message to be sent
    });
  });

  // clear any announcement
  $('.announce .remove').click(function() {
    $(this).parents('.announce').remove();
  });

}(jQuery));
