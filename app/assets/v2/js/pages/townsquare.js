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

  // updates expiry timers with countdowns
  var updateTimers = function() {
    $('.timer').each(function() {
      var time = $(this).data('time');

      $(this).html(time_difference_broken_down(new Date(time) - new Date()));
    });
  };

  setInterval(updateTimers, 1000);

  // toggles the daily email sender
  $('#receive_daily_offers_in_inbox').on('change', function(e) {
    _alert('Your email subscription preferences have been updated', 'success', 2000);

    var url = '/api/v0.1/emailsettings/';
    var params = {
      'new_bounty_notifications': $(this).is(':checked')
    };

    $.post(url, params, function(response) {
      // no message to be sent
    });
  });

}(jQuery));
