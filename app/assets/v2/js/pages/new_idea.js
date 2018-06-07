$('document').ready(() => {

  initCharCounter('#summary', '#summary_chars');
  initCharCounter('#more_info', '#more_info_chars');
  
});

function initCharCounter(inputId, counterElementId) {
  $(inputId).keyup(function() {
    $(counterElementId).text($(this).val().length);
  });
}
