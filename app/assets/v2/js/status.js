$(document).ready(function() {
  last_video = '';
  let button = document.querySelector('#btn_post');

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

  // dropdown for usernames when @ is detected in the post
  $('#textarea').on('input', function(e) {
    const lastWord = e.target.value.split(' ').pop();
    const youtube_re = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
    const url = e.target.value.match(youtube_re);
    let videoId;

    if (url)
      videoId = url[7].slice(0, 11);

    if (url && videoId.length === 11) {
      if (last_video !== videoId) {
        var apiKey = ''; // TODO: add youtube API key to query titles

        let getVideoData = fetchData('https://www.googleapis.com/youtube/v3/videos?key=' + apiKey + '&fields=items(snippet(title))&part=snippet&id=' + videoId);

        $.when(getVideoData).then(function(response) {
          if (response.items.length !== 0) {
            $('#thumbnail-title').text(response.items[0].snippet.title);
            $('#thumbnail-provider').text('Youtube');
            $('#thumbnail-img').attr('src', 'https://img.youtube.com/vi/' + videoId + '/default.jpg');

            last_video = videoId;
            $('#thumbnail').show();
          } else {
            $('#thumbnail').hide();
            last_video = '';
          }
        });
      }
    } else {
      $('#thumbnail').hide();
      last_video = '';
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
              let userRow = $('<a class="dropdown-item" href="#"></a>');

              userRow.append(`<img class="rounded-circle" src="${avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="20" height="20"/>`);
              userRow.append(`<span>${handle}</span>`);

              userRow.click(function(e) {
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

  if ($('#textarea').length) {
    $('#textarea').focus();
  }

  $('body').on('focus change paste keyup blur', '#textarea', function(e) {

    // enforce a max length
    var max_len = $(this).data('maxlen');

    if ($(this).val().trim().length > max_len) {
      e.preventDefault();
      $(this).addClass('red');
      var old_val = $(this).val();

      setTimeout(function() {
        $('#textarea').val(old_val.slice(0, max_len));
      }, 20);
    } else {
      $(this).removeClass('red');
    }

    // enable post via enter button
    if ($(this).val().trim().length > 4) {
      $('#btn_post').attr('disabled', false);
      if ($('#textarea').is(':focus') && (e.keyCode == 13)) {
        submitStatusUpdate();
        e.preventDefault();
      }
    } else {
      $('#btn_post').attr('disabled', true);
    }
  });

  function submitStatusUpdate() {
    const data = new FormData();
    const message = $('#textarea');
    const ask = $('.activity_type_selector .active input').val();

    data.append('ask', ask);
    data.append('data', message.val().trim());
    data.append('what', $('#status [name=what]').val());
    message.val('');
    data.append(
      'csrfmiddlewaretoken',
      $('#status input[name="csrfmiddlewaretoken"]').attr('value')
    );

    if (last_video) {
      data.append('resource', 'video');
      data.append('resourceProvider', 'youtube');
      data.append('resourceId', last_video);
    }

    fetch('/api/v0.1/activity', {
      method: 'post',
      body: data
    })
      .then(response => {
        if (response.status === 200) {
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
          $('#thumbnail').hide();
        } else {
          _alert(
            { message: gettext('An error occurred. Please try again.') },
            'error'
          );
        }
      })
      .catch(err => console.log('Error ', err));
  }
});
