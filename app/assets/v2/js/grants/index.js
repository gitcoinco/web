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
    }
  });

  $('.flip-card').on('click keypress', e => {
    if ($(e.target).is('a') || $(e.target).is('img')) {
      e.stopPropagation();
      return;
    }
    $(e.currentTarget).toggleClass('turn');
  });
});
