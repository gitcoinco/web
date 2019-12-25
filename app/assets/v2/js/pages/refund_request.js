$(document).ready(function() {
  if (!caseInsensitiveCompare($('#bounty_owner').html(), document.contxt.github_handle)) {
    $('.metamask-banner').hide();
    $('#primary_form').hide();
    $('#wrong_owner').show();
  } else {
    $('#primary_form').show();
  }

  $('#submitRequest').on('click', function(event) {
    event.preventDefault();
    let csrftoken = $("input[name='csrfmiddlewaretoken']").val();

    const data = {
      'comment': $('#refund_reason').val()
    };

    $.ajax({
      type: 'post',
      url: '?pk=' + $('#pk').val(),
      data: data,
      headers: {'X-CSRFToken': csrftoken},
      success: () => {
        $('#primary_form').hide();
        $('#success_container').show();
      },
      error: (e) => {
        console.log(e);

        _alert({ message: 'Something went wrong submitting your request. Please try again.'}, 'error');
      }
    });
  });
});