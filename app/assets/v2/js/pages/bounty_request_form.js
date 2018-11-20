
// Overwrite from shared.js
var trigger_form_hooks = function() {
  callFunctionWhenweb3Available(
    function() {
      const addr = web3.eth.coinbase;
      const input = $('[name=eth_address]');

      if (addr && !input.val()) {
        input.val(addr);
      }
    }
  );
};

$(document).ready(function() {
  if (document.comments_prefill) {
    $('[name=comment]').val(document.comments_prefill);
  }

  $('[for=id_comment]').append(
    ' (<span id="charcount">500</span> ' + gettext('characters left') + ')'
  );
  $('[name=comment]').bind('input propertychange', function() {
    this.value = this.value.replace(/ +(?= )/g, '');

    if (this.value.length > 500) {
      this.value = this.value.substring(0, 500);
    }

    $('#charcount').html(500 - this.value.length);

  });

  const form = $('#bounty_request_form');

  form.validate({
    submitHandler: function(form) {
      const inputElements = $(form).find(':input');
      const formData = {};

      inputElements.removeAttr('disabled');
      $.each($(form).serializeArray(), function() {
        formData[this.name] = this.value;
      });

      inputElements.attr('disabled', 'disabled');
      loading_button($('.js-submit'));

      const payload = JSON.stringify(formData);

      $.post('/requests', payload).then(
        function(result) {
          inputElements.removeAttr('disabled');
          $('#requested_by').attr('disabled', 'disabled');
          unloading_button($('.js-submit'));

          $('#primary_form').hide();
          $('#success_container').show();
        }
      ).fail(
        function(result) {
          inputElements.removeAttr('disabled');
          $('#requested_by').attr('disabled', 'disabled');
          unloading_button($('.js-submit'));

          var alertMsg = result && result.responseJSON ? result.responseJSON.error : null;

          if (alertMsg === null) {
            alertMsg = gettext('Network error. Please reload the page and try again.');
          }

          _alert({ message: alertMsg }, 'error');
        }
      );
    }
  });
});
