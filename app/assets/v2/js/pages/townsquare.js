$(document).ready(function() {
  // gets multi part (ex: 10 hours 2 minutes 5 seconds) time
  var time_difference_broken_down = function(difference) {
    let remaining = ' now. Refresh to view offer!';
    let prefix = ' in ';

    if (difference > 0) {
      console.log(moment(difference).inspect());
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

  $('.top_offer').click(function(e) {
    document.location = $(this).find('a.btn').attr('href');
  });

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
  $('body').on('click', '.townsquare_nav-list .nav-link', function(e) {
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    e.preventDefault();
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
  });
  // updates expiry timers with countdowns

  const updateTimers = function() {
    let enterTime = moment();

    $('[data-time]').filter(':visible').each(function() {
      moment.locale('en');
      var time = $(this).data('time');
      var base_time = $(this).data('base_time');
      var timeFuture = $(this).data('time-future');
      var counter = $(this).data('counter');

      if (!counter) {
        counter = 0;
      }
      counter += 1;
      $(this).data('counter', counter);
      // var start_date = new Date(new Date(time).getTime() - (1000 * counter));

      // var countdown = start_date - new Date(base_time);

      // console.log(countdown, new Date(new Date(time).getTime() - (1000 * counter))- new Date(base_time), start_date.diff(enterTime,'min'))


      // console.log(moment(time).diff(enterTime,'min'), time)
      // console.log(timeUrl && moment(time).diff(enterTime,'min') > 0)
      //       if (timeUrl && ( moment(time).diff(enterTime,'min') > 0)) {
      //         let btn = `<a class="btn btn-block btn-gc-blue btn-sm mt-2" href="${timeUrl}">View Action</a>`;
      //         console.log(btn)
      //         return $(this).parent().next().html(btn);
      //       }
      // enterTime < time {
      //   fromNow() is future
      // }
      // $(this).html(time_difference_broken_down(countdown));
      // console.log(moment.utc(time).fromNow(), moment.utc(time).inspect(), moment.relativeTimeThreshold('s'))
      var timeDiff = moment(time).diff(enterTime, 'sec');

      if (timeFuture && (timeDiff < 0)) {
        console.log(moment(time).diff(enterTime, 'sec'), $(this));
        $(this).html('now');
        $(this).parents('.offer_container').addClass('animate');
        return $(this).parent().next().html('Refresh to view offer!');
      }
      $(this).html(moment.utc(time).fromNow());
    });
  };

  setInterval(updateTimers, 1000);

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
