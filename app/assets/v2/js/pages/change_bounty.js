
// Overwrite from shared.js
// eslint-disable-next-line no-empty-function
function trigger_form_hooks() {
}

$(document).ready(function() {
  const oldBounty = document.result;
  const keys = Object.keys(oldBounty);
  const form = $('#submitBounty');
  var bounty_reserved_for = {};

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
  
  $('#reservedFor').on('select2:select', function(e) {
    
    var data = e.params.data;
    bounty_reserved_for = {
      username: data.text,
      creation_date: new Date(),
      email: data.email,
      avatar_url: ''
    };
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
      // update bounty reserved for
      formData.bounty_reserved_for = bounty_reserved_for;

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
