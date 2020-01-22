/* eslint-disable no-console */

$(document).ready(function() {

  $('input[name="session_date"]').daterangepicker({
    singleDatePicker: true,
    autoUpdateInput: false
  }, function(chosen_date) {
    $('input[name="session_date"]').val(chosen_date.format('YYYY-MM-DD'));
  });

});
