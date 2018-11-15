const editableFields = [
  '#form--input__title',
  '#form--input__reference-url',
  '#grant-admin',
  '#form--input__description',
  '#grant-members'
];

$(document).ready(function() {
  $('#tabs').tabs();

  $('#form--input__description').height($('#form--input__description').prop('scrollHeight'));

  userSearch('#grant-admin');
  userSearch('#grant-members');

  $('.select2-selection__rendered').removeAttr('title');
  $('#form--input__description').height($('#form--input__description').prop('scrollHeight'));

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

    // TODO : Loop through editableFields -> form object with value -> fire save API

    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel-details').on('click', (event) => {
    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');

    // TODO: Reset value
    editableFields.forEach(field => disableEdit(field));
  });

  $('#js-cancel_grant').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      web3.eth.getAccounts(function(err, accounts) {


        deployedSubscription.methods.endContract().send({from: accounts[0], gasPrice: 4000000000})
          .on('confirmation', function(confirmationNumber, receipt) {
            console.log('receipt', receipt);

            form.submit();
          });

      });
    }
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