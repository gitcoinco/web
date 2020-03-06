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

  $('#mobile_nav_toggle li a').click(function(e) {
    $('#mobile_nav_toggle li a').removeClass('active');
    $(this).addClass('active');
    if ($(this).data('slug') == 'feed') {
      $('.feed_container').removeClass('hidden');
      $('.actions_container').addClass('hidden');
    } else {
      $('.feed_container').addClass('hidden');
      $('.actions_container').removeClass('hidden');
    }
  });

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
    let personal = $('#personal').is(':checked') ? 1 : 0;

    return '/?tab=' + tab + '&trending=' + trending + '&personal=' + personal;
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
  $('body').on('click', '#personal', function(e) {
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
  });
  $('body').on('click', '.townsquare_nav-list .nav-link', function(e) {
    if ($(this).attr('href') != '#') {
      return;
    }
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    e.preventDefault();
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
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

  function onIntersection(imageEntites, observer) {
    imageEntites.forEach(image => {
      if (image.isIntersecting) {
        observer.unobserve(image.target);
        image.target.src = image.target.dataset.src;
        image.target.onload = () => image.target.classList.add('loaded');
      }
    });
  }
  const interactSettings = {
    root: document.querySelector('.loader-container'),
    rootMargin: '0px 200px 200px 200px',
    threshold: 0.01
  };

  function loadImages() {
    if ('IntersectionObserver' in window) {
      let images = [...document.querySelectorAll("img[loading='lazy']")];
      let observer = new IntersectionObserver(onIntersection, interactSettings);

      images.forEach(img => {
        img.setAttribute('loading', '');
        observer.observe(img);
      });
    } else {
      const images = document.querySelectorAll("img[loading='lazy']");

      images.forEach(img => {
        img.src = img.dataset.src;
        img.setAttribute('loading', '');
      });
    }

    window.setTimeout(loadImages, 700);
  }

  loadImages();
}(jQuery));
