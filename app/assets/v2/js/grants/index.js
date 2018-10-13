$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });

  $('.select2-selection__rendered').hover(() => {
    $(this).removeAttr('title');
  });
});