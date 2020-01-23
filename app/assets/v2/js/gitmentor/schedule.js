/* eslint-disable no-console */

$(document).ready(function() {

  $('input[name="session_datetime"]').daterangepicker({
    singleDatePicker: true,
    timePicker: true,
    timePicker24Hour: true,
    timePickerIncrement: 5,
    autoUpdateInput: false
  }, function(chosen_date) {
    $('input[name="session_datetime"]').val(chosen_date.format('YYYY-MM-DD hh:mm'));
  });

  userSearch('.mentor', false, undefined, false, false, true);
});
