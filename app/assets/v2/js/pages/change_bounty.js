
// Overwrite from shared.js
// eslint-disable-next-line no-empty-function
function trigger_form_hooks() {
}

$(document).ready(function() {
  const oldBounty = document.result;
  const keys = Object.keys(oldBounty);
  const form = $('#submitBounty');

  while (keys.length) {
    const key = keys.pop();
    const val = oldBounty[key];
    const ele = form.find('[name=' + key + ']');

    ele.val(val);
    ele.find(
      'option:contains(' + val + ')'
    ).prop('selected', true);
  }

  $('.js-select2').each(function() {
    $(this).select2();
  });

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

      mixpanel.track('Change Bounty Details Clicked', {});

      const bountyId = document.pk;
      const payload = JSON.stringify(formData);

      $.post('/bounty/change/' + bountyId, payload).then(
        function(result) {
          inputElements.removeAttr('disabled');
          unloading_button($('.js-submit'));

          result = sanitizeAPIResults(result);
          _alert({ message: result.msg }, 'success');

          if (result.url) {
            setTimeout(function() {
              document.location.href = result.url;
            }, 1000);
          }
        }
      ).fail(
        function(result) {
          inputElements.removeAttr('disabled');
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
