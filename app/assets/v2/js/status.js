const url_re = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,10}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/;
const youtube_re = /(?:https?:\/\/|\/\/)?(?:www\.|m\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})(?![\w-])/;
const giphy_re = /(?:https?:\/\/)?(?:media0\.)?(?:giphy\.com\/media\/)/;

$(document).ready(function() {
  var embedded_resource = '';
  const GIPHY_API_KEY = '1WfeOI2i4lJiBKvO2Q1W3yUqdjQ27UTy';
  
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
        
        let downsize = item.images.downsized.url;
        let preview = item.images.fixed_width_downsampled.url;

        $('.gif-grid').append('<img class="lazy pick-gif" src="' + preview + '" data-src="' + downsize + '" alt="' + item.slug + '">');
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

  // dropdown for usernames when @ is detected in the post
  $('#textarea').on('input', function(e) {
    e.preventDefault();
    const lastWord = e.target.value.split(' ').pop();
    const site = e.target.value.match(url_re);
    const youtube = e.target.value.match(youtube_re);
    const no_lb = e.originalEvent.inputType !== 'insertLineBreak';
    
    if (typeof embedded_resource === 'string' && embedded_resource.match(giphy_re)) {
      return;
    }
    
    if (youtube !== null && youtube[1].length === 11 && no_lb) {
      let videoId = youtube[1];
      
      if (embedded_resource !== youtube[0]) {
        var apiKey = 'AIzaSyDi-EFpC2ntx9PnM_-oiJHk5zCY53KdIf0'; // TODO: add youtube API key to query titles

        let getVideoData = fetchData('https://www.googleapis.com/youtube/v3/videos?key=' + apiKey + '&fields=items(snippet(title))&part=snippet&id=' + videoId);

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
      let url = site[0];
      
      let getMetadata = fetchData('service/metadata/?url=' + url);

      $.when(getMetadata).then(function(response) {
        if (response) {
          $('#thumbnail-title').text(response.title);
          $('#thumbnail-provider').text(response.link);
          $('#thumbnail-desc').text(response.description);
          $('#thumbnail-img').attr('src', response.image);

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
          _alert(
            { message: gettext('An error occurred. Please try again.') },
            'error'
          );
        }
      })
      .catch(err => console.log('Error ', err));
  }
  
  injectGiphy('latest');
});
