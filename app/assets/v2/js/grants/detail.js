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
        console.log('save details POST successful');
      },
      error: function() {
        console.log('save details POST failure');
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

  $('#cancel_grant').click(function() {

    let contract_address = $('#contract_address').val();

    let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, contract_address);

    web3.eth.getAccounts(function(err, accounts) {
      deployedSubscription.methods.endContract()
        .send({from: accounts[0], gasPrice: 4000000000})
        .on('transactionHash', function() {
          enableWaitState('#grants-details');
        })
        .on('confirmation', function(confirmationNumber, receipt) {
          $.ajax({
            type: 'post',
            url: '',
            data: { 'contract_address': contract_address},
            success: function(json) {
              console.log('cancel grant POST successful');
            },
            error: function() {
              console.log('failure');
            }
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
