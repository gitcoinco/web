$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });
  $('.select2-selection__rendered').removeAttr('title');

  $('#search_from').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      form.submit();
  })
});
