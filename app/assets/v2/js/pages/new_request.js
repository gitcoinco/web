window.onload = function() {
  $('#js-new-bounty-request').validate({
    submitHandler: function(form, event) {
      event.preventDefault();

      var action = $(form).attr('action');
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      form.submit(data);
    }
  });
};
