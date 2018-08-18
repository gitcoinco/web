$(document).ready(function() {
  $('.checkbox .checkbox-label').click(function() {
    var this_text = $(this).text();

    $('form#search_form input[name=q]').val(this_text);
    $('form#search_form').submit();
  });
});
