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

  $('body').on('click', '#mobile_nav_toggle li a', function(e) {
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

  $('body').on('click', '.close-promo', function(e) {
    e.preventDefault();
    $('.promo').remove();
    localStorage.setItem('hide_promo', true);
  });

  $('body').on('click', '.top_offer', function(e) {
    document.location = $(this).find('a.btn').attr('href');
  });

  // collapse menu items
  $('body').on('click', '.townsquare_block-header', function(e) {
    let target_id = $(this).data('target');

    $('#' + target_id).toggleClass('hidden');
    $(this).toggleClass('closed');
    localStorage.setItem(target_id, $(this).hasClass('closed'));
  });

  // effects when an offer is clicked upon
  $('body').on('click', '.offer a', function(e) {
    var speed = 500;

    $(this).addClass('clicked');
    $(this).find('#ribbon').effect('puff', speed, function() {
      $(this).find('#giftbox').effect('puff', speed);
    });
  });

  var get_redir_location = function(tab) {
    let trending = $('#trending').is(':checked') ? 1 : 0;
    let personal = $('#personal').is(':checked') ? 1 : 0;

    return '/townsquare?tab=' + tab + '&trending=' + trending + '&personal=' + personal;
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
  $('body').on('change', '#receive_daily_offers_in_inbox', function(e) {
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
  $('body').on('click', '.announce .remove', function() {
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

  var load_dressing = function() {
    var url = document.location.href;

    url = url + (url.indexOf('?') == -1 ? '?' : '&') + 'dressing=1';
    $.get(url, function(response) {

      // load content
      $('#right_sidebar').html($(response).find('#right_sidebar').html());
      $('#left_sidebar').html($(response).find('#left_sidebar').html());
      $('#top_bar').html($(response).find('#top_bar').html());
      // bind more actions
      joinTribe();
      // collapse menu items
      $('.townsquare_block-header').each(function() {
        let target_id = $(this).data('target');
        var item = localStorage.getItem(target_id);

        if (item == 'true') {
          $(this).click();
        }
      });
      const hide_promo = localStorage.getItem('hide_promo');

      if (!hide_promo) {
        $('.promo').removeClass('hidden');
      }
    });
  };

  load_dressing();
}(jQuery));
