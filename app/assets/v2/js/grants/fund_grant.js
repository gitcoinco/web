/* eslint-disable no-console */
window.onload = function() {
  $('#period').select2();

  $('.js-select2').each(function() {
    $(this).select2();
  });

  $('#js-fundGrant').validate({
    submitHandler: function(form) {
      var action = $(form).attr('action');
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      console.log(data);

      form.submit();
    }
  });
};
