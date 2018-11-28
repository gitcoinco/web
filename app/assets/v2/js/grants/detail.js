const editableFields = [
  '#form--input__title',
  '#form--input__reference-url',
  '#grant-admin',
  '#form--input__description',
  '#grant-members'
];

function getCookie(name) {
  var cookieValue = null;

  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');

    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?

      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }
  }
});

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

  $('#cancel_grant').click(function() {

    let contract_address = $('#contract_address').val();

    $.ajax({
      type: 'post',
      url: '',
      data: { 'contract_address': contract_address},
      success: function(json) {
        console.log('requested access complete');
      },
      error: function() {
        console.log('failure');
      }
    });

    // let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, contract_address);
    //
    //    web3.eth.getAccounts(function(err, accounts) {
    //
    //      deployedSubscription.methods.endContract().send({from: accounts[0], gasPrice: 4000000000})
    //        .on('confirmation', function(confirmationNumber, receipt) {
    //          console.log('receipt', receipt);
    //
    //
    //
    //        });
    //
    //    });
  });

  // $('#js-cancel_grant').validate({
  //   submitHandler: function(form) {
  //     var data = {};
  //
  //     $.each($(form).serializeArray(), function() {
  //       data[this.name] = this.value;
  //     });
  //
  //     let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);
  //
  //     web3.eth.getAccounts(function(err, accounts) {
  //
  //       deployedSubscription.methods.endContract().send({from: accounts[0], gasPrice: 4000000000})
  //         .on('confirmation', function(confirmationNumber, receipt) {
  //           console.log('receipt', receipt);
  //
  //           form.submit();
  //         });
  //
  //     });
  //   }
  // });

  $('#js-edit_grant').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      console.log('data', data);

      form.submit();
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
