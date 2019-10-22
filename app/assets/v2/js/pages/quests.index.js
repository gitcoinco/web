
$(document).ready(function() {

  $('#reflink').click(function() {
    $(this).focus();
    $(this).select();
    document.execCommand('copy');
    $(this).after('<div class=after_copy>Copied to clipboard</div>');
    setTimeout(function() {
      $('.after_copy').remove();
    }, 500);
  });

  $('.demo').click(function(e) {
    e.preventDefault();
    $(this).fadeOut(function() {
      $('.demo').fadeIn();
      var src = $('.demo').attr('src') + '?';

      $('.demo').attr('src', src);
    });
  });
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

  $('#tabs a').click(function(e) {
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

  $('.quest-card.available').click(function(e) {
    e.preventDefault();
    document.location.href = $(this).find('a').attr('href');
  });
  $('.quest-card.available').mouseover(function(e) {
    random_attn_effect($(this).find('.btn'));
  });

});
