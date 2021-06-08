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
    if (web3Modal && !web3Modal.cachedProvider) {
      onConnect().then(() => {
        trigger_faucet_form_web3_hooks(provider);
      });
      return false;
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

var trigger_faucet_form_web3_hooks = function(data) {
  if (!data) {
    return;
  }
  let cb_address = data.selectedAddress;

  if ($('#faucet_form').length) {
    $('#ethAddress').val(cb_address);
    var faucet_amount = parseInt($('#currentFaucet').val() * (Math.pow(10, 18)));

    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    } else if (!cb_address) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'block');
      $('#connect_metamask_error').css('display', 'none');
      $('#over_balance_error').css('display', 'none');
      $('#faucet_form').addClass('hidden');
      return;
    } else if (balance >= faucet_amount) {
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#over_balance_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
    } else {
      $('#over_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#faucet_form').removeClass('hidden');
    }
  }
  if ($('#admin_faucet_form').length) {
    if (typeof web3 == 'undefined') {
      $('#no_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    }
    if (!cb_address) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#faucet_form').addClass('hidden');
      return;
    }
    web3.eth.getBalance(cb_address, function(errors, result) {
      if (errors) {
        return;
      }

      if (!result.toNumber()) {
        $('#zero_balance_error').css('display', 'block');
        $('#admin_faucet_form').remove();
      }
    });
  }
};

needWalletConnection();
window.addEventListener('dataWalletReady', function(e) {
  // BN = web3.utils.BN;
  trigger_faucet_form_web3_hooks(provider);
}, false);
