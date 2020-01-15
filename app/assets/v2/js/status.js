$(document).ready(function() {
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

  if ($('#textarea').length) {
    $('#textarea').focus();
  }

  $('body').on('focus change paste keyup blur', '#textarea', function(e) {

    // enforce a max length
    var max_len = 280;

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
});
