
$('.modal-link').click(function(e) {
  let modals = $('#modal');
  let modalBody = $('#modal .modal-content');
  let modalUrl = `/modal/social_contribution?pk=${document.result.pk}`;

  modals.on('show.bs.modal', function() {
    modalBody.load(modalUrl, ()=> {
      userSearch('.users_share');
      copyClipboard();
      $('#sendInvites').on('click', () =>{
        let users = $('.users_share').data('select2').data();

        sendInvites(users);
      });
    });
  });
  e.preventDefault();
});

const sendInvites = (users) => {
  let usersId = [];
  let msg = $('#shareText').val();
  const bountyId = document.result.pk;

  $.each(users, function(index, elem) {
    usersId.push(elem.id);
  });

  var sendEmail = fetchData(
    '/api/v0.1/social_contribution_email/',
    'POST',
    {usersId, msg, bountyId, invite_url},
    {'X-CSRFToken': csrftoken}
  );

  $.when(sendEmail).then(
    function(payback) {
      _alert('The invitation has been sent', 'info');
      $('.users_share').val(null).trigger('change');
      return payback;
    }
  );
};

