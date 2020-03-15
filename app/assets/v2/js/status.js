const url_re = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,10}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/;
const youtube_re = /(?:https?:\/\/|\/\/)?(?:www\.|m\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})(?![\w-])/;
const giphy_re = /(?:https?:\/\/)?(?:media0\.)?(?:giphy\.com\/media\/)/;

$(document).ready(function() {
  var embedded_resource = '';
  const GIPHY_API_KEY = document.contxt.giphy_key;

  let button = document.querySelector('#btn_post');

  function selectGif(e) {
    embedded_resource = $(e.target).data('src');
    $('#preview-img').attr('src', embedded_resource);
    $('#preview').show();
    $('#thumbnail').hide();
  }


  function injectGiphy(query) {
    const endpoint = 'https://api.giphy.com/v1/gifs/search?limit=13&api_key=' + GIPHY_API_KEY + '&offset=0&rating=G&lang=en&q=' + query;
    const result = fetchData(endpoint);

    $.when(result).then(function(response) {
      $('.pick-gif').remove();

      for (let i = 0; i < response.data.length; i++) {
        let item = response.data[i];
        let downsize = item.images.original.webp;
        let preview = item.images.fixed_width_downsampled.webp;

        $('.gif-grid').append('<img class="pick-gif" src="' + preview + '" data-src="' + downsize + '" alt="' + item.slug + '">');
      }
      $('.pick-gif').on('click', selectGif);
    });
  }

  $('#search-gif').on('input', function(e) {
    e.preventDefault();
    const query = e.target.value;

    injectGiphy(query);
  });

  if (button) {
    button.addEventListener(
      'click',
      function() {
        submitStatusUpdate();
      },
      false
    );
  }

  $('#textarea, #btn_post').click(function(e) {
    if (!document.contxt.github_handle) {
      e.preventDefault();
      _alert('Please login first.', 'error');
      return;
    }
  });

  // cache activity/status for if u leave page
  var lskey = 'activity_' + document.location.href;
  var current_ls_activity = localStorage.getItem(lskey);

  if (current_ls_activity) {
    $('#textarea').val(current_ls_activity);
  }

  // dropdown for usernames when @ is detected in the post
  $('#textarea').on('input', function(e) {
    e.preventDefault();
    const lastWord = e.target.value.split(' ').pop();
    const site = e.target.value.match(url_re);
    const youtube = e.target.value.match(youtube_re);
    const no_lb = e.originalEvent.inputType !== 'insertLineBreak';

    // GIF has priority, no other display info allowed
    if (typeof embedded_resource === 'string' && embedded_resource.match(giphy_re)) {
      return;
    }

    if (youtube !== null && youtube[1].length === 11 && no_lb) {
      let videoId = youtube[1];

      if (embedded_resource !== youtube[0]) {
        var apiKey = document.contxt.youtube_key; // TODO: add youtube API key to query titles

        const getVideoData = fetchData('https://www.googleapis.com/youtube/v3/videos?key=' + apiKey + '&fields=items(snippet(title))&part=snippet&id=' + videoId);

        $.when(getVideoData).then(function(response) {
          if (response.items.length !== 0) {
            $('#thumbnail-title').text(response.items[0].snippet.title);
            $('#thumbnail-provider').text('Youtube');
            $('#thumbnail-img').attr('src', 'https://img.youtube.com/vi/' + videoId + '/default.jpg');
            embedded_resource = youtube[0];
            $('#thumbnail').show();
            $('#preview').hide();
          } else {
            $('#thumbnail').hide();
            $('#thumbnail-desc').text('');
            embedded_resource = '';
          }
        });
      }
    } else if (site && site.length > 1 && no_lb) {
      const url = site[0];

      const getMetadata = fetchData('service/metadata/?url=' + url);

      $.when(getMetadata).then(function(response) {
        if (response) {
          const desc = response.description && response.description.length > 200 ?

            response.description.substr(0, 200) + '...' :
            response.description;

          $('#thumbnail-title').text(response.title);
          $('#thumbnail-provider').text(response.link);
          $('#thumbnail-desc').text(desc);
          if (response.image) {
            $('#thumbnail-img').attr('src', response.image);
            $('#thumbnail-img').removeClass('py-2 px-4');
            $('#thumbnail-img').css('width', '130%');
          } else {
            $('#thumbnail-img').addClass('py-2 px-4');
            $('#thumbnail-img').css('width', '8rem');
            $('#thumbnail-img').attr('src', 'https://s.gitcoin.co/static/v2/images/team/gitcoinbot.c1e81ab42f13.png');
          }

          embedded_resource = url;
          $('#thumbnail').show();
          $('#preview').hide();
        } else {
          $('#thumbnail').hide();
          $('#thumbnail-desc').text('');
          embedded_resource = '';
        }
      });
    } else {
      $('#thumbnail-desc').text('');
      if (no_lb) {
        embedded_resource = '';
        $('#thumbnail').hide();
      }
    }

    if (/\B@([a-zA-Z0-9_-]{2})/g.test(lastWord)) {
      const usernameFilter = lastWord.slice(1);

      function split(val) {
        // replace comma with space: https://stackoverflow.com/a/24826141/678481
        return val.split(/ \s*/);
      }
      function extractLast(term) {
        return split(term).pop();
      }

      $.ui.autocomplete.prototype._resizeMenu = function() {
        this.menu.element.css({'left': 'initial'});
      }

      $('#textarea').on('keydown', function(event) {
        // don't navigate away from the field on tab when selecting an item
        if (event.keyCode === $.ui.keyCode.TAB && $(this).autocomplete("instance").menu.active) {
          event.preventDefault();
        }
      }).autocomplete({
        source: function (request, response) {
          $.getJSON(`/api/v0.1/users_fetch/?search=${usernameFilter}`, function(data) {
            response($.map(data.data, function(value, key) {
              // return {handle: value.handle, avatar_url: value.avatar_url};
              return value.handle;
            }));
          });
        },
        minLength: 2,
        delay: 250,
        autoFocus: true,
        search: function(event, ui) {
          // custom minLength
          let term = extractLast(this.value);
          if (term.length < 2) {
            return false;
          }
        },
        focus: function () {
          // prevent value inserted on focus
          return false;
        },
        select: function(event, ui) {
          let terms = split(this.value);

          // remove the current input
          terms.pop();
          // add the selected item
          terms.push(`@${ui.item.value}`);
          // add placeholder to get the comma-and-space at the end
          terms.push('');
          this.value = terms.join(' ');

          return false;
        },
        classes: {
            "ui-autocomplete": "dropdown-menu",
            "ui-menu-item": "dropdown-item"
        },
      });

      return;
    }
  });

  if ($('#textarea').length && $('#textarea').offset().top < 400) {
    $('#textarea').focus();
  }

  document.is_shift = false;
  // handle shift button
  $('body').on('keyup', '#textarea', function(e) {
    if (e.keyCode == 16) {
      document.is_shift = false;
    }
  });

  // handle shift button
  $('body').on('click', '#poll-button', function(e) {
    e.preventDefault();
    $(this).toggleClass('selected');
    var is_selected = $(this).hasClass('selected');

    if (is_selected) {
      let html = `
      <div id=poll_container class="bg-lightblue p-2">
      <input name=option1 placeholder="Option 1" class="form-control form-control-sm my-2">
      <input name=option2 placeholder="Option 2" class="form-control form-control-sm my-2">
      <input name=option3 placeholder="Option 3" class="form-control form-control-sm my-2">
      <input name=option4 placeholder="Option 4" class="form-control form-control-sm my-2">
      </div>
      `;

      $(html).insertAfter('#status');
      $('#poll_container input[name=option1]').focus();
    } else {
      $('#poll_container').remove();
    }

  });
  $('body').on('keydown', '#textarea', function(e) {
    if (e.keyCode == 16) {
      document.is_shift = true;
    }
  });

  $('body').on('focus change paste keydown keyup blur', '#textarea', function(e) {

    // enforce a max length
    var max_len = $(this).data('maxlen');
    var len = $(this).val().trim().length;

    var update_max_len = function() {
      if ($('#char_count').length) {
        if (len < max_len) {
          $('#char_count').addClass('hidden');
        } else {
          $('#char_count').removeClass('hidden');
        }
        $('#char_count').text(len + '/' + max_len);
      }
    };

    update_max_len();
    localStorage.setItem(lskey, $(this).val());
    if ($(this).val().trim().length > max_len) {
      $(this).addClass('red');
      $('#btn_post').attr('disabled', true);
    } else if (len > 4) {
      $('#btn_post').attr('disabled', false);
      $(this).removeClass('red');
      if ($('#textarea').is(':focus') && !e.shiftKey && e.keyCode == 13) {
        submitStatusUpdate();
        e.preventDefault();
      }
    } else {
      $('#btn_post').attr('disabled', true);
    }
  });

  function submitStatusUpdate() {
    if ($('#btn_post').is(':disabled')) {
      return;
    }
    const data = new FormData();
    const message = $('#textarea');
    const the_message = message.val().trim();
    const ask = $('.activity_type_selector .active input').val();

    data.append('ask', ask);
    data.append('data', the_message);
    data.append('what', $('#status [name=what]').val());
    data.append('tab', getParam('tab'));

    message.val('');
    localStorage.setItem(lskey, '');
    data.append(
      'csrfmiddlewaretoken',
      $('input[name="csrfmiddlewaretoken"]').attr('value')
    );

    if (embedded_resource) {
      const title = $('#thumbnail-title').text();
      const link = $('#thumbnail-provider').text();
      const description = $('#thumbnail-desc').text();
      const image = $('#thumbnail-img').attr('src');
      const youtube = embedded_resource.match(youtube_re);

      if (embedded_resource.match(giphy_re)) {
        data.append('resource', 'gif');
        data.append('resourceProvider', 'giphy');
        data.append('resourceId', embedded_resource);
      } else if (youtube !== null && youtube[1].length === 11) {
        data.append('resource', 'video');
        data.append('resourceProvider', 'youtube');
        data.append('resourceId', youtube[1]);
        data.append('title', title);
        data.append('description', description);
        data.append('image', image);
      } else {
        data.append('resource', 'content');
        data.append('resourceProvider', link);
        data.append('resourceId', embedded_resource);
        data.append('title', title);
        data.append('description', description);
        data.append('image', image);
      }
    }

    var fail_callback = function() {
      message.val(the_message);
      localStorage.setItem(lskey, the_message);
      _alert(
        { message: gettext('An error occurred. Please try again.') },
        'error'
      );
    };

    for (let i = 0; i < 5; i++) {
      const val = $('#poll_container input[name=option' + i + ']').val();

      if (val) {
        data.append('option' + i, val);
      }
    }
    $('#poll_container').remove();

    fetch('/api/v0.1/activity', {
      method: 'post',
      body: data
    })
      .then(response => {
        if (response.status === 200) {
          $('#thumbnail').hide();
          $('#thumbnail-title').text('');
          $('#thumbnail-provider').text('');
          $('#thumbnail-desc').text('');
          $('#thumbnail-img').attr('src', '');
          $('#preview').hide();
          $('#preview-img').attr('src', '');
          embedded_resource = '';

          _alert(
            { message: gettext('Status has been saved.') },
            'success',
            1000
          );
          const activityContainer = document.querySelector('.tab-section.active .activities');

          if (!activityContainer) {
            document.run_long_poller(false);
            // success
            return;
          }
          activityContainer.setAttribute('page', 0);
          $('.tab-section.active .activities').html('');
          message.val('');
        } else {
          fail_callback();
        }
      })
      .catch(err => fail_callback());
  }

  injectGiphy('latest');
});
window.addEventListener('DOMContentLoaded', function() {
  var button = document.querySelector('#emoji-button');
  var picker = new EmojiButton({
    position: 'left-end'
  });

  if (button && picker) {
    picker.on('emoji', function(emoji) {
      document.querySelector('textarea').value += emoji;
    });

    button.addEventListener('click', function() {
      picker.pickerVisible ? picker.hidePicker() : picker.showPicker(button);
    });
  }
});
