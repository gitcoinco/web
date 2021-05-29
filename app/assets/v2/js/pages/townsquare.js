$(document).ready(function() {

  let resizeTimeout = null;

  const collapseAccordions = function() {
    const window_width = $('body').width();

    $('.townsquare_block-header').each(function(e) {
      const target_id = $(this).data('target');
      const item = localStorage.getItem(target_id.replace(/^#/, ''));

      // if we're heading into md breakpoint then close the accordions
      // if we're heading out of md breakpoint then open any closed accordions that should be open
      if (window_width <= breakpoint_lg && item && item !== 'false' && !$(this).hasClass('collapsed')) {
        // tigger collapse but don't save the state change
        $(this).trigger('click', true);
      } else if (window_width > breakpoint_lg && item && item !== 'false' && $(this).hasClass('collapsed')) {
        // tigger expand but don't save the state change
        $(this).trigger('click', true);
      }
    });
    if (window_width > breakpoint_md) {
      $('#mobile_nav_toggle li a').removeClass('active');
      $('.feed_container,.actions_container').removeClass('hidden');
    }
  };

  // debounce the resize event
  window.addEventListener('resize', function() {
    // clear the timeout
    clearTimeout(resizeTimeout);
    // start timing for event "completion"
    resizeTimeout = setTimeout(collapseAccordions, 30);
  });

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

  // effects when an offer is clicked upon
  $('body').on('click', '.offer a', function(e) {
    const speed = 500;

    $(this).addClass('clicked');
    $(this).find('#ribbon').effect('puff', speed, function() {
      $(this).find('#giftbox').effect('puff', speed);
    });
  });

  const get_redir_location = function(tab) {
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

  // collapse menu items
  $('body').on('click', '.townsquare_block-header', function(e, triggered) {
    const target_id = $(this).data('target');

    if (!triggered) {
      localStorage.setItem(target_id.replace(/^#/, ''), $(this).hasClass('collapsed'));
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

    const url = '/api/v0.1/emailsettings/';
    const params = {
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

  const load_dressing = function() {
    let url = document.location.href.replace('#', '');

    url = url + (url.indexOf('?') == -1 ? '?' : '&') + 'dressing=1';
    console.log('url is', url);
    $.get(url, function(response) {

      // load content
      $('#right_sidebar').html($(response).find('#right_sidebar').html());
      $('#left_sidebar').html($(response).find('#left_sidebar').html());
      $('#top_bar').html($(response).find('#top_bar').html());

      if (document.contxt.github_handle) {
        appOnboard.profileWidget();
      } else if (document.getElementById('profile-completion')) {
        document.getElementById('profile-completion').parentElement.remove();
      }

      // bind more actions
      joinTribe();
      const hide_promo = localStorage.getItem('hide_promo');

      if (!hide_promo) {
        $('.promo').removeClass('hidden');
      }
      $('.townsquare_block-header').each(function() {
        const target_id = $(this).data('target');
        const item = localStorage.getItem(target_id.replace(/^#/, ''));

        if ($('body').width() > breakpoint_lg) {
          if (item && item == 'true') {
            $(this).removeClass('collapsed');
            $(target_id).addClass('show');
          }
        }
      });
    });
  };

  load_dressing();
}(jQuery));
