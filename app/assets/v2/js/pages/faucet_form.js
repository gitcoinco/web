$('document').ready(function() {

  $('#comment').bind('input propertychange', function() {
    this.value = this.value.replace(/ +(?= )/g, '');

    if (this.value.length > 500) {
      this.value = this.value.substring(0, 500);
    }

    if (this.value.length) {
      $('#charcount').html(501 - this.value.length);
    }

  });

  $('#githubProfile').on('focus', function() {
    $('#githubProfileHelpBlock').hide();
    $('#githubProfile').removeClass('is-invalid');
  });

  $('#emailAddress').on('focus', function() {
    $('#emailAddressHelpBlock').hide();
    $('#emailAddress').removeClass('is-invalid');
  });

  $('#emailAddress').on('change', function() {
    var exp = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

    if (!exp.test(this.value)) {
      $('#emailAddress').addClass('is-invalid');
      $('#emailAddressHelpBlock').html(gettext('We could not validate that input as an email address')).show();
    }
  });

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return ((/^(GET|HEAD|OPTIONS|TRACE)$/).test(method));
  }
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
    }
  });

  $('#submitFaucet').on('click', function(e) {
    e.preventDefault();
    if (document.web3network != 'mainnet') {
      _alert({ message: gettext('you must be on mainnet')}, 'error');
      return;
    }
    if ($(this).hasClass('disabled')) {
      return;
    }
    $('#submitFaucet').addClass('disabled');

    if (e.target.hasAttribute('disabled') ||
       $('#githubProfile').is(['is-invalid']) ||
       $('#emailAddress').is(['is-invalid']) ||
       $('#githubProfile').val() === '' ||
       $('#emailAddress').val() === '') {
      _alert(gettext('Please make sure to fill out all fields.'));
      $('#submitFaucet').removeClass('disabled');
      return;
    }

    var faucetRequestData = {
      'githubProfile': $('#githubProfile').val().replace('@', ''),
      'ethAddress': $('#ethAddress').val(),
      'emailAddress': $('#emailAddress').val(),
      'comment': $('#comment').val()
    };

    $.post('/api/v0.1/faucet/save', faucetRequestData)
      .done(function(d) {
        $('#primary_form').hide();
        $('#success_container').show();
        $('#submitFaucet').removeClass('disabled');
      })

      .fail(function(response) {
        var message = gettext('Got an unexpected error');

        if (response && response.responseJSON && response.responseJSON.message) {
          message = response.responseJSON.message;
        }
        $('#submitFaucet').removeClass('disabled');
        $('#primary_form').hide();
        $('#fail_message').html(message);
        $('#fail_container').show();
      });
  });
});
