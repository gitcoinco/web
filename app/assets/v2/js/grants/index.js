$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });
  $('.select2-selection__rendered').removeAttr('title');
});