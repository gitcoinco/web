$('body').on('click', '[data-open-rating] input', function(e) {
  ratingModal($(this).parent().data('openRating'), $(this).parent().data('openUsername'), $(this));
});

const ratingModal = (bountyId, receiver, elem) => {
  let modalUrl = `/modal/rating/${bountyId}/${receiver}`;

  $.ajax({
    url: modalUrl,
    type: 'GET',
    cache: false
  }).done(function(result) {
    $('body').append(result);
    $('#modalRating').bootstrapModal('show');
    $('[data-toggle="tooltip"]').bootstrapTooltip();
    $('input[name="review[rating]"]').filter('[value="' + elem.val() + '"]').prop('checked', true);

    $('#ratingForm').on('submit', function(e) {
      e.preventDefault();
      let data = $(this).serializeArray();
      let sendRating = fetchData ('/postcomment/', 'POST', data);

      $.when(sendRating).then(response => {
        if (!response.success) {
          return _alert(response.msg, 'error');
        }
        elem.closest('fieldset').attr('disabled', true);

        $('#modalRating').bootstrapModal('hide');
        return _alert({message: gettext('Thanks for your feedback.')}, 'info');
      });
    });
  });

  $(document, '#modalRating').on('hidden.bs.modal', function(e) {
    let value = $('input[name="review[rating]"]:checked').val();

    elem.siblings('input').filter('[value="' + value + '"]').prop('checked', true);
    $('#modalRating').remove();
    $('#modalRating').bootstrapModal('dispose');
  });
};
