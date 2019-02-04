
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

  $.each(users, function(index, elem) {
    usersId.push(elem.id);
  });

  var sendEmail = fetchData ('/api/v0.1/ENDPOING/','POST', {usersId, msg})
  $.when(sendEmail).then(
    function(payback) {
      return payback
    }
  );
  console.log(usersId, msg);
};

