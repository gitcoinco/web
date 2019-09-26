$(document).ready(function() {
  $('#newkudos input.btn-go').click(function(e) {
    mixpanel.track('New Kudos Request', {});
    setTimeout(function() {
      $('#newkudos input.btn-go').attr('disabled', 'disabled');
    }, 1);
  });
});