$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });

  $('#network').select2({
    minimumResultsForSearch: Infinity
  });


  $('#sort_option').on("change", function (e) {
    // Should this fire POST / Update URL + fire ajax ?
  });

  $('#network').on("change", function (e) {
    // Should this fire POST / Update URL + fire ajax ?
  });

  $('.select2-selection__rendered').removeAttr('title');

  $('#search_form').validate({
    submitHandler: (form) => {
      let data = {};

      $.each($(form).serializeArray(), () => {
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
