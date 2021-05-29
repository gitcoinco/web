
const url_re = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,10}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/;
const youtube_re = /(?:https?:\/\/|\/\/)?(?:www\.|m\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})(?![\w-])/;
const giphy_re = /(?:https?:\/\/)?(?:media0\.)?(?:giphy\.com\/media\/)/;

$(document).ready(function() {

  var embedded_resource = '';
  const GIPHY_API_KEY = document.contxt.giphy_key;

  let button = document.querySelector('#btn_post');

  // populates background selector on load
  let bgs = [
    'cannon-green-blue',
    'h2-v2',
    'burst-yellow',
    'burst-pink',
    'burst-blue',
    'eletric_design',
    'dvdptr-blue-green',
    'cannon-yellow-pink',
    'network-yellow',
    'h4',
    'network-blue',
    'network-pink',
    'h2',
    'cannon-blue-yellow',
    'dvdptr-blue-yellow'
  ];

  let selector = $('#bg-selector');

  for (var i = 0; i < bgs.length; i++) {
    selector.append('<div data-bg-name="' + bgs[i] + '" class="bg-thumbnail"><img class="bg-icon" draggable="false" src="/static/status_backgrounds/' + bgs[i] + '-icon.png"/><div class="selector-bar d-none"></div></div>');
  }

  function closeBackgroundDropdown(e) {
    e.preventDefault();
    $('#bg-selector').attr('data-selected', null);
    embedded_resource = '';
  }

  function selectGif(e) {
    embedded_resource = $(e.target).data('src');
    $('#preview-img').attr('src', embedded_resource);
    $('#preview').show();
    $('#thumbnail').hide();
  }

  function deselectGif(e) {
    embedded_resource = '';
    $('#preview-img').attr('src', '');
    $('#preview').hide();
    $('#thumbnail').hide();
    $('#btn_gif').removeClass('selected');
    $('.gif-inject-target').removeClass('show');
  }

  function deselectVideo(e) {
    $('#video-button').removeClass('selected');
    $('#video_container').remove();
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

        $('.gif-grid').append('<img width="300" class="pick-gif" src="' + preview + '" data-src="' + downsize + '" alt="' + item.slug + '">');
      }
      $('.pick-gif').on('click', selectGif);
    });
  }

  $('#btn_gif').on('click', function(e) {
    window.setTimeout(function() {
      $('#search-gif').focus();
      console.log($('#search-gif'));
    }, 100);

    if (!$('.pick-gif').length) {
      injectGiphy('latest');
    }
  });

  $('#search-gif').on('input', function(e) {
    e.preventDefault();
    const query = e.target.value;

    injectGiphy(query);
    if (!query) {
      injectGiphy('latest');
    }
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
      _alert('Please login first.', 'danger');
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

      let metadata_callback = function(response) {
        document[url] = response;
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
      };
      // cache calls for the same URL on the document

      if (typeof document[url] == 'undefined') {
        const getMetadata = fetchData('service/metadata/?url=' + url);

        $.when(getMetadata).then(metadata_callback);
      } else {
        metadata_callback(document[url]);
      }
    } else {
      $('#thumbnail-desc').text('');
      if (no_lb) {
        if (embedded_resource != $('#bg-selector').attr('data-selected')) {
          embedded_resource = '';
        }
        $('#thumbnail').hide();
      }
    }

    if (lastWord.startsWith('@')) {
      const usernameFilter = lastWord.slice(1);

      if (usernameFilter.length > 2) {
        const api = `/api/v0.1/users_fetch/?search=${usernameFilter}`;
        let getUsers = fetchData(api, 'GET');

        $.when(getUsers).then(function(response) {
          let dropdown = $('#textarea-dropdown');

          dropdown.empty();

          if (response.data && response.data.length) {
            for (profile of response.data) {
              const { avatar_url, handle } = profile;
              let userRow = $('<a class="dropdown-item" tabindex="0" href="#"></a>');

              userRow.append(`<img class="rounded-circle mr-1" src="${avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="20" height="20"/>`);
              userRow.append(`<span>${handle}</span>`);

              userRow.click(function(e) {
                e.preventDefault();
                let inputVal = $('#textarea').val();
                let inputPos = inputVal.search(lastWord);

                if (inputPos !== -1) {
                  let newVal = inputVal.slice(0, inputPos) + '@' + handle + ' ';

                  $('#textarea').val(newVal);
                  $('#textarea').focus();
                  $('#textarea-dropdown').removeClass('show');
                }
              });
              dropdown.append(userRow);
            }
          } else {
            dropdown.append(`No username matching '${usernameFilter}'`);
          }

          dropdown.addClass('show');
        });
      }
      return;
    }

    $('#textarea-dropdown').removeClass('show');
  });

  $('#textarea').focusout(function(e) {
    window.setTimeout(function() {
      $('#textarea-dropdown').removeClass('show');
    }, 100);
  });

  if ($('#textarea').length && $('#textarea').offset().top < 400) {
    $('#textarea').focus();
  }

  $('#btn_gif').click(function(e) {
    e.preventDefault();
    closeBackgroundDropdown(e);
    deselectVideo(e);

    $('#poll-button').removeClass('selected');
    $('#poll_container').remove();
  });

  var selectedElement = null;
  // handle background selection

  $('.bg-thumbnail').click(function(e) {
    e.preventDefault();

    $('#bg-selector').find('.selector-bar').addClass('d-none');
    $(this).children('div').removeClass('d-none');

    selectedElement = $(this);
    $('#bg-selector').attr('data-selected', $(this).attr('data-bg-name'));
    embedded_resource = $(this).attr('data-bg-name');
  });

  // handle add background button push
  $('body').on('click', '#background-button', function(e) {
    e.preventDefault();
    $('#bg-selector').toggleClass('d-none');
    if ($('#bg-selector').hasClass('d-none')) {
      closeBackgroundDropdown(e);
    }

    $('#poll-button').removeClass('selected');
    $('#poll_container').remove();
    deselectVideo(e);
    deselectGif(e);
  });


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
    deselectGif(e);
    closeBackgroundDropdown(e);
    deselectVideo(e);
    $(this).toggleClass('selected');
    var is_selected = $(this).hasClass('selected');

    if (is_selected) {
      let html = `
        <div id=poll_container class="bg-lightblue p-2">
          <input name=option1 placeholder="Option 1" class="form-control form-control-sm">
          <input name=option2 placeholder="Option 2" class="form-control form-control-sm">
          <input name=option3 placeholder="Option 3" class="form-control form-control-sm">
          <input name=option4 placeholder="Option 4" class="form-control form-control-sm">
        </div>
      `;

      $(html).insertAfter('#status');
      $('#poll_container input[name=option1]').focus();
    } else {
      $('#poll_container').remove();
    }

  });

  // handle video button
  $('body').on('click', '#video-button', function(e) {
    e.preventDefault();
    closeBackgroundDropdown(e);
    deselectGif(e);
    $('#poll-button').removeClass('selected');
    $('#poll_container').remove();

    $(this).toggleClass('selected');
    var is_selected = $(this).hasClass('selected');

    if (is_selected) {
      const items = [ 'video1.gif', 'video2.gif', 'video3.png' ];
      const item = $(this).data('gfx') ? $(this).data('gfx') : items[Math.floor(Math.random() * items.length)];

      let html = `
        <div data-gfx=` + item + ` id=video_container class="bg-lightblue p-2">
        <img src='/static/v2/images/` + item + `'>
        </div>
        `;

      $(html).insertAfter('#status');
    } else {
      $('#video_container').remove();
    }


    document.is_shift = false;
    // handle shift button
    $('body').on('keyup', '#textarea', function(e) {
      if (e.keyCode == 16) {
        document.is_shift = false;
      }
    });


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
      if ($('#textarea').is(':focus') && e.shiftKey && e.keyCode == 13) {
        submitStatusUpdate();
        e.preventDefault();
      }
    } else {
      $('#btn_post').attr('disabled', true);
    }
  });

  $('#btn_attach').on('click', function() {
    const el = $('#attach-dropdown');

    el.toggle();
  });


  function submitStatusUpdate() {
    if ($('#btn_post').is(':disabled')) {
      return;
    }

    if (typeof ga !== 'undefined') {
      ga('send', 'event', 'Submit Status Update', 'click', 'Person');
    }

    const data = new FormData();
    const message = $('#textarea');
    const the_message = message.val().trim();
    const ask = $('.activity_type_selector input:checked').val();
    const tab = document.current_tab || '';

    data.append('ask', ask);
    data.append('data', the_message);
    data.append('what', $('#status [name=what]').val());
    data.append('tab', tab);
    if ($('#video_container').length) {
      data.append('has_video', $('#video_container').length);
      data.append('video_gfx', $('#video_container').data('gfx'));
    }

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
      const background = $('#bg-selector').attr('data-selected');

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
      } else if (background != null) {
        data.append('resource', 'background');
        data.append('resourceProvider', 'gitcoin');
        data.append('resourceId', background);
      } else {
        data.append('resource', 'content');
        data.append('resourceProvider', link);
        data.append('resourceId', embedded_resource);
        data.append('title', title);
        data.append('description', description);
        data.append('image', image);
      }
    }

    const attach = $('#attach-dropdown')[0].style.display;
    const amount = $('#attachAmount').val();
    const address = $('#attachToken').val();
    const token_name = $('#attachToken :selected').text();

    $('#bg-selector').attr('data-selected', null);
    $('#bg-selector').addClass('d-none');
    $('#bg-selector').children('div').children('div').addClass('d-none');

    var fail_callback = function() {
      message.val(the_message);
      localStorage.setItem(lskey, the_message);
      _alert(
        { message: gettext('An error occurred. Please try again.') },
        'error'
      );
    };

    const success_callback = function(txid) {
      const url = 'https://' + etherscanDomain() + '/tx/' + txid;
      const msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

      _alert(msg, 'info', 1000);

      data.append('attachTxId', txid);
      fetch('/api/v0.1/activity', {
        method: 'post',
        body: data
      }).then(response => {
        if (response.status === 200) {
          $('#thumbnail').hide();
          $('#thumbnail-title').text('');
          $('#thumbnail-provider').text('');
          $('#thumbnail-desc').text('');
          $('#thumbnail-img').attr('src', '');
          $('#preview').hide();
          $('#preview-img').attr('src', '');
          $('#attach-dropdown').hide();
          $('#attachAmount').val('');

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
          _alert(
            { message: gettext('An error occurred. Please try again.') },
            'error'
          );
        }
      }).catch(err => fail_callback());
    };

    const failure_callback = function() {
      $.noop(); // do nothing
    };

    if (!isNaN(parseFloat(amount)) && address) {
      data.append('attachToken', address);
      data.append('attachAmount', amount);
      data.append('attachTokenName', token_name);
      const email = '';
      const github_url = '';
      const from_name = document.contxt['github_handle'];
      const username = '';
      const amountInEth = amount;
      const comments_priv = '';
      const comments_public = '';
      const from_email = '';
      const accept_tos = true;
      const tokenAddress = address;
      const expires = 9999999999;

      sendTip(
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
        false,
        true // No available user to send tip at this moment
      );

    } else {
      for (let i = 0; i < 5; i++) {
        const val = $('#poll_container input[name=option' + i + ']').val();

        if (val) {
          data.append('option' + i, val);
        }
      }

      $('#poll_container').remove();
      $('#video_container').remove();

      fetch('/api/v0.1/activity', {
        method: 'post',
        body: data
      }).then(response => {
        if (response.status === 200) {
          $('#thumbnail').hide();
          $('#thumbnail-title').text('');
          $('#thumbnail-provider').text('');
          $('#thumbnail-desc').text('');
          $('#thumbnail-img').attr('src', '');
          $('#preview').hide();
          $('#preview-img').attr('src', '');
          $('#attach-dropdown').hide();
          $('#attachAmount').val('');
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
      }).catch(err => fail_callback());
    }
  }

});
window.addEventListener('DOMContentLoaded', function() {

  $(() => {
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
});
