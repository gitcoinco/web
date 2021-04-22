
// Overwrite from shared.js
var trigger_form_hooks = function() {
  callFunctionWhenweb3Available(
    function() {
      web3.eth.getCoinbase(function(_, addr) {
        const input = $('[name=eth_address]');

        if (addr && !input.val()) {
          input.val(addr);
        }
      });
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
      let githubOrgName = '';

      inputElements.removeAttr('disabled');
      $.each($(form).serializeArray(), function() {
        if (this.name === 'github_url') {
          formData['github_url'] = this.value;

          const url = new URL(this.value);
          const urlParts = url.pathname.split('/');

          githubOrgName = urlParts[1] || '';
          formData['github_org_name'] = githubOrgName;
        } else if (this.name !== 'github_org_name') {
          // Ignore 'github_org_name' value from the form as this is already handled 2 lines above
          formData[this.name] = this.value;
        }
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

          _alert({ message: alertMsg }, 'danger');
        }
      );
    }
  });
});
