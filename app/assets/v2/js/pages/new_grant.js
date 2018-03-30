/* eslint-disable no-console */
window.onload = function() {
  $('#js-newGrant').validate({
    submitHandler: function(form) {
      var data = {};
      var disabled = $(form)
        .find(':input:disabled')
        .removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

    }
  });
};
