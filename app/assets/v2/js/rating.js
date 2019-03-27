$('[data-open-rating] input').on('click', function(e) {
  ratingModal($(this).parent().data('openRating'), $(this));
});

const ratingModal = (bountyId, val) => {
  let modalUrl = `/modal/rating/${bountyId}`;

  $.ajax({
    url: modalUrl,
    type: 'GET',
    cache: false
  }).done(function(result) {
    $('body').append(result);
    $('#modalRating').bootstrapModal('show');
    $('[data-toggle="tooltip"]').runTooltip();
    $('input[name="rating"]').filter('[value="' + val.val() + '"]').prop('checked', true);

    $('#ratingForm').on('submit', function(e) {
      e.preventDefault();
      let data = $(this).serializeArray();
      let sendRating = fetchData ('/postcomment/', 'POST', data);

      $.when(sendRating).then(response => {
        val.closest('fieldset').attr('disabled', true);
        if (!response.success) {
          return _alert(response.msg, 'error');
        }

        $('#modalRating').bootstrapModal('hide');
        return _alert({message: gettext('Thanks for your feedback.')}, 'info');
      });
    });
  });

  $(document, '#modalRating').on('hidden.bs.modal', function(e) {
    // let selected = $('input[name="rating"]:checked').val()
    // console.log('closing', val.parent(), $('input[name="rating"]:checked').val())
    // $('input[name="'+ val[0].name +'"]').filter('[value="'+ $('input[name="rating"]:checked').val() +'"]').prop('checked', true)

    $('#modalRating').remove();
    $('#modalRating').bootstrapModal('dispose');
  });
};
