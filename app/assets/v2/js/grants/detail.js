const editableFields = [
  '#form--input__title',
  '#form--input__reference-url',
  '#grant-admin',
  '#form--input__description',
  '#grant-members'
];

$(document).ready(function() {
  $('#tabs').tabs();

  userSearch('#grant-admin');
  userSearch('#grant-members');

  $('.select2-selection__rendered').removeAttr('title');
  $('#form--input__description').height($('#form--input__description').prop('scrollHeight'));
  $('#form--input__title').height($('#form--input__title').prop('scrollHeight'));
  $('#form--input__reference-url').height($('#form--input__reference-url').prop('scrollHeight'));

  $('#edit-details').on('click', (event) => {
    event.preventDefault();

    $('#edit-details').addClass('hidden');
    $('#save-details').removeClass('hidden');
    $('#cancel-details').removeClass('hidden');

    editableFields.forEach(field => {
      makeEditable(field);
    });

  });

  $('#save-details').on('click', (event) => {
    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');

    let edit_title = $('#form--input__title').val();
    let edit_reference_url = $('#form--input__reference-url').val();
    let edit_admin_profile = $('#grant-admin option').last().text();
    let edit_description = $('#form--input__description').val();
    let edit_grant_members = $('#grant-members').val();

    $.ajax({
      type: 'post',
      url: '',
      data: {
        'edit-title': edit_title,
        'edit-reference_url': edit_reference_url,
        'edit-admin_profile': edit_admin_profile,
        'edit-description': edit_description,
        'edit-grant_members[]': edit_grant_members
      },
      success: function(json) {
        window.location.reload(false);
      },
      error: function() {
        alert('Your edits failed to save. Please try again.');
      }
    });

    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel-details').on('click', (event) => {
    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');

    // TODO: Reset value
    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel_grant').on('click', function(e) {
    var img_src = static_url + 'v2/images/grants/cancel-grants-icon.png';
    var content = $.parseHTML(
      '<div>' +
        '<div class="row px-5">' +
          '<div class="col-12 closebtn">' +
            '<a rel="modal:close" href="javascript:void" class="close" aria-label="Close dialog">' +
              '<span aria-hidden="true">&times;</span>' +
            '</a>' +
          '</div>' +
          '<div class="col-12 pt-2 pb-2 text-center">' +
            '<h2 class="font-title">' + gettext('Are you sure you want to cancel this grant?') + '</h2>' +
          '</div>' +
          '<div class="col-12 text-center">' +
            '<img src="' + img_src + '" />' +
          '</div>' +
          '<div class="col-12 pt-2 pb-2 font-body">' +
            '<p>' + gettext('By clicking Cancel, you will be cancelling this grant from Gitcoin.') + '</p>' +
            '<ul><li>' + gettext('Your grant will stay in Gitcoin, but ') + '<b>' + gettext('marked as inactive.') + '</b></li>' +
            '<li>' + gettext('Funds received till now ') + '<b>' + gettext('will not be refunded ') + '</b>' + gettext('to the contributors.') + '</li>' +
            '<li>' + gettext('Once cancelled, it is ') + '<b>' + gettext('not possible to restart the grant, ') + '</b>' + gettext('as the smart contract will be destroyed.') + '</li></ul>' +
            '<p>' + gettext('To relaunch the grant, you need to create a new grant.') + '</p>' +
          '</div>' +
          '<div class="col-12 mt-4 mb-2 text-right font-caption">' +
            '<a rel="modal:close" href="javascript:void" aria-label="Close dialog" class="button button--primary-o mr-3">' + gettext('No, I don\'t want to cancel') + '</a>' +
            '<button class="modal-cancel-grants button button--warning">' + gettext('Cancel this Grant') + '</button>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
    var modal = $(content).appendTo('#js-cancel_grant').modal({
      modalClass: 'modal cancel_grants'
    });

    $('.modal-cancel-grants').on('click', function(e) {
      let contract_address = $('#contract_address').val();
      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, contract_address);

      web3.eth.getAccounts(function(err, accounts) {
        deployedSubscription.methods.endContract()
          .send({from: accounts[0], gasPrice: 4000000000})
          .on('transactionHash', function() {
            document.issueURL = document.getElementById('form--input__reference-url').value;
            $('.modal .close').trigger('click');
            enableWaitState('#grants-details');
          })
          .on('confirmation', function(confirmationNumber, receipt) {
            $.ajax({
              type: 'post',
              url: '',
              data: { 'contract_address': contract_address},
              success: function(json) {
                window.location.reload(false);
              },
              error: function() {
                alert('Canceling you grant failed to save. Please try again.');
              }
            });
          });
      });
    });
  });

});

const makeEditable = (input, icon) => {
  $(input).addClass('editable');
  $(input).prop('readonly', false);
  $(input).prop('disabled', false);
};

const disableEdit = (input) => {
  $(input).removeClass('editable');
  $(input).prop('readonly', true);
  $(input).prop('disabled', true);
};
