$(document).ready(function() {

  $('.demo').click(function(e) {
    e.preventDefault();
    $(this).fadeOut(function() {
      $('.demo').fadeIn();
      var src = $('.demo').attr('src') + '?';

      $('.demo').attr('src', src);
    });
  });

  $(document).on('submit', '#search_form', function(e) {
    e.preventDefault();
    var q = $(this).find('input').val();

    $('.loading').removeClass('hidden');
    $('.difficulty_tab').addClass('hidden');
    $('.quest-card').addClass('hidden');
    var callback = function() {
      $('#search_form input').val(q).focus();
    };

    load_quests(q, callback);
  });

  var load_quests = function(term, callback) {
    var url = '/quests/?show_quests=1&q=' + (term ? term : '');

    focused_hackathon = getParam('focus_hackathon');
    if (focused_hackathon) {
      url += '&focus_hackathon=' + focused_hackathon;
    }

    $.get(url, function(response) {
      $('#available_quests').html($(response).find('#available_quests').html());
      if (callback) {
        callback();
      }
    });
  };

  load_quests(null, null);

  var random_attn_effect = function(ele) {
    if (ele.data('effect')) {
      return;
    }
    ele.data('effect', 1);
    var r = Math.random();

    if (r < 0.3) {
      ele.effect('highlight');
    } else if (r < 0.6) {
      ele.effect('bounce');
    } else {
      ele.effect('highlight');
    }
    setTimeout(function() {
      ele.data('effect', 0);
    }, 1000);
  };

  $(document).on('click', '#tabs a', function(e) {
    e.preventDefault();
    var target = $(this).data('href');

    $('.difficulty_tab').addClass('hidden');
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    $('.difficulty_tab.' + target).removeClass('hidden');

    $('html,body').animate({
      scrollTop: '+=1px'
    });
  });

  $('#leaderboard_tabs a').click(function(e) {
    e.preventDefault();
    var target = $(this).data('href');

    $('.leaderboard_tab').addClass('hidden');
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    $('.' + target).removeClass('hidden');

    $('html,body').animate({
      scrollTop: '+=1px'
    });
  });

  $('.quest-card.available').mouseover(function(e) {
    random_attn_effect($(this).find('.btn'));
  });

  const observerOptions = {
    rootMargin: '0px 0px 200px 0px',
    threshold: 0
  };

  function preloadImage(image) {
    const src = image.getAttribute('data-src');

    if (!src) {
      return;
    }
    image.src = src;
  }

  let observer = new IntersectionObserver(function(entries, self) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        preloadImage(entry.target);
        self.unobserve(entry.target);
      }
    });
  }, observerOptions);

  let images = document.querySelectorAll('[data-src]');

  images.forEach(image => {
    observer.observe(image);
  });

  setTimeout(function() {
    $('.leaderboard_hero').css('background-image', 'url("{% static \'v2/images/kudos/kudos-bg.png\' %}")');
  }, 1000);
});
