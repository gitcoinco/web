$(document).ready(function() {

  $('#theme').on('change', function(e) {
    e.preventDefault();
    document.location.href = $(this).val();
  });

  $('#skin_tones li:nth-child(1)').addClass('selected');
  $('#hair_tones li:nth-child(1)').addClass('selected');
  $('.tdselection:first-child').addClass('selected');
  document.td_ids = [];
  document.skin_tone = $('#skin_tones li.selected').data('tone');
  document.hair_tone = $('#hair_tones li.selected').data('tone');

  var get_avatar_url = function() {
    var url = '/avatar/view3d?';

    for (var i = 0; i < document.td_ids.length; i += 1) {
      url += '&ids[]=' + document.td_ids[i];
    }
    var st = document.skin_tone;
    var ht = document.hair_tone;

    if (typeof st == 'undefined') {
      st = '';
    }
    if (typeof ht == 'undefined') {
      ht = '';
    }
    url += '&skinTone=' + st;
    url += '&hairTone=' + ht;
    var theme = getParam('theme');

    if (!theme) {
      theme = 'unisex';
    }
    url += '&theme=' + theme;
    return url;
  };

  $('.tdselection').click(function(e) {
    e.preventDefault();
    var sel = $(this).hasClass('selected');

    $(this).parents('.category').find('.selected').removeClass('selected');
    if (sel) {
      $(this).removeClass('selected');
    } else {
      $(this).addClass('selected');
    }
    document.td_ids = [];
    $('.tdselection.selected').each(function() {
      document.td_ids.push($(this).data('id'));
    });
    $('#tdavatartarget').attr('src', get_avatar_url());
  });

  $('#skin_tones li').click(function(e) {
    e.preventDefault();
    $(this).parents('#skin_tones').find('.selected').removeClass('selected');
    $(this).addClass('selected');
    document.skin_tone = $(this).data('tone');
    update_all_options();
  });

  var update_all_options = function() {
    $('#tdavatartarget').attr('src', get_avatar_url());
    $('.tdselection').each(function() {
      var st = document.skin_tone;
      var ht = document.hair_tone;

      if (typeof st == 'undefined') {
        st = '';
      }
      if (typeof ht == 'undefined') {
        ht = '';
      }
      var new_url = $(this).data('src') + '&skinTone=' + st + '&hairTone=' + ht;

      $(this).data('altsrc', new_url);
      $(this).attr('src', '');
    });
    $('.tdselection:visible').each(function() {
      $(this).attr('src', $(this).data('altsrc'));
    });
  };

  $('#hair_tones li').click(function(e) {
    e.preventDefault();
    $(this).parents('#hair_tones').find('.selected').removeClass('selected');
    $(this).addClass('selected');
    document.hair_tone = $(this).data('tone');
    update_all_options();
  });


  $('#random-3d-avatar-button').click(function(e) {
    e.preventDefault();
    $('.select_avatar_type').each(function() {
      var catclass = $(this).data('target');

      $('.category.' + catclass + ' .tdselection').random().click();
    });
    $('#skin_tones li').random().click();
    $('#hair_tones li').random().click();
  });


  $('.select_avatar_type').click(function(e) {
    e.preventDefault();
    var target = $(this).data('target');

    $('.select_avatar_type').removeClass('active');
    $(this).addClass('active');
    $('#avatars-builder-3d .category').addClass('hidden');
    $('#avatars-builder-3d .' + target).removeClass('hidden');
    $('#avatars-builder-3d .' + target + ' img').each(function() {
      if (!$(this).attr('src')) {
        var src = $(this).data('altsrc');

        $(this).attr('src', src);
      }
    });
  });
  $('.select_avatar_type:first').click(); // set default tab

  function save3DAvatar() {
    $(document).ajaxStart(function() {
      loading_button($('#save-3d--avatar'));
    });

    $(document).ajaxStop(function() {
      unloading_button($('#save-3d-avatar'));
    });

    var url = get_avatar_url();
    var request = $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify({save: true}),
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      success: function(response) {
        _alert({ message: gettext('Your Avatar Has Been Saved To your Gitcoin Profile!')}, 'success');
        changeStep(1);
      },
      error: function(response) {
        let text = gettext('Error occurred while saving. Please try again.');

        if (response.responseJSON && response.responseJSON.message) {
          text = response.responseJSON.message;
        }
        $('#later-button').show();
        _alert({ message: text}, 'error');
      }
    });
  }
  $('#save-3d-avatar').click(function() {
    save3DAvatar();
  });


  jQuery.fn.random = function() {
    var randomIndex = Math.floor(Math.random() * this.length);

    return jQuery(this[randomIndex]);
  };

});