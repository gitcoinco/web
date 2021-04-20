$(document).ready(function() {
  $('#newkudos input.btn-go').click(function(e) {
    mixpanel.track('New Kudos Request', {});
    setTimeout(function() {
      $('#newkudos input.btn-go').attr('disabled', 'disabled');
    }, 1);
  });
  $('input[type="file"]').change(function(e) {
    var fileName = e.target.files[0].name;

    if (fileName.indexOf('.svg') == -1) {
      _alert('The file format is not an svg... svg is the only supported file format.  Please convert to svg and resubmit', 'danger');
    }
  });
});
