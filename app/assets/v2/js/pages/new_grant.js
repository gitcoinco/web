/* eslint-disable no-console */
window.onload = function() {
  $('#js-newGrant').validate({
    submitHandler: function(form) {
      var action = $(form).attr('action');
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });
    }

    $(form).submit();
  });
};
