/* eslint-disable no-console */

$(document).ready(function() {

  $('[data-form-method]').on('click', function(event) {
    event.preventDefault();
    event.stopPropagation();

    var form = $(this).parents('form:first');

    var method = $(this).attr('data-form-method');

    form.find('input[name="method"]').val(method);

    if (method == 'PUT') {
      form.validate();
    }

    form.submit();
  });

});
