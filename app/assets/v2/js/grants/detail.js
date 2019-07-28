const editableFields = [
  '#form--input__title',
  '#form--input__reference-url',
  '#grant-admin',
  '#contract_owner_address',
  '#grant-members',
  '#amount_goal'
];

$(document).ready(function() {
  showMore();
  addGrantLogo();

  setInterval (() => {
    notifyOwnerAddressMismatch(
      $('#grant-admin').val(),
      $('#grant_contract_owner_address').text(),
      '#cancel_grant',
      'Looks like your grant has been created with ' +
        $('#grant_contract_owner_address').text() + '. Switch to take action on your grant.'
    );

    if ($('#cancel_grant').attr('disabled')) {
      $('#cancel_grant').addClass('disable-btn').addClass('disable-tooltip');
      $('#cancel_grant_tooltip').attr(
        'data-original-title', 'switch to below contract owner address to cancel grant.'
      );
    } else {
      $('#cancel_grant').removeClass('disable-btn').removeClass('disable-tooltip');
      $('#cancel_grant_tooltip').attr('data-original-title', '');
    }

    if ($('#contract_owner_address').val() === $('#grant_contract_owner_address').text()) {
      $('#contract_owner_button').attr('disabled', true);
      $('#contract_owner_button').addClass('disable-btn').addClass('disable-tooltip');
      $('#contract_owner_button-container').attr(
        'data-original-title', 'Grant owner address hasn\'t changed. Update the above field to enable this.'
      );
    } else {
      $('#contract_owner_button').attr('disabled', false);
      $('#contract_owner_button').removeClass('disable-btn').removeClass('disable-tooltip');
      $('#contract_owner_button-container').attr('data-original-title', '');
    }
  }, 1000);

  let _text = grant_description.getContents();

  userSearch('#grant-admin', false, undefined, false, false, true);
  userSearch('#grant-members', false, undefined, false, false, true);
  $('.select2-selection__rendered').removeAttr('title');
  $('#form--input__title').height($('#form--input__title').prop('scrollHeight'));
  $('#form--input__reference-url').height($('#form--input__reference-url').prop('scrollHeight'));

  $('#edit-details').on('click', (event) => {
    event.preventDefault();

    if (grant_description) {
      grant_description.enable(true);
      grant_description.getContents();
    }
    $('#edit-details').addClass('hidden');
    $('#save-details').removeClass('hidden');
    $('#cancel-details').removeClass('hidden');
    $('#contract_owner_button').removeClass('hidden');
    $('#edit-amount_goal').removeClass('hidden');
    $('.grant__progress').addClass('hidden');

    copyDuplicateDetails();

    editableFields.forEach(field => {
      makeEditable(field);
    });

  });

  $('#save-details').on('click', (event) => {
    if (grant_description) {
      grant_description.enable(false);
    }

    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');
    $('#edit-amount_goal').addClass('hidden');
    $('.grant__progress').removeClass('hidden');

    let edit_title = $('#form--input__title').val();
    let edit_reference_url = $('#form--input__reference-url').val();
    let edit_admin_profile = $('#grant-admin option').last().text();
    let edit_description = grant_description.getText();
    let edit_description_rich = JSON.stringify(grant_description.getContents());
    let edit_amount_goal = $('#amount_goal').val();
    let edit_grant_members = $('#grant-members').val();

    $.ajax({
      type: 'post',
      url: '',
      data: {
        'edit-title': edit_title,
        'edit-reference_url': edit_reference_url,
        'edit-admin_profile': edit_admin_profile,
        'edit-description': edit_description,
        'edit-description_rich': edit_description_rich,
        'edit-amount_goal': edit_amount_goal,
        'edit-grant_members[]': edit_grant_members
      },
      success: function(json) {
        window.location.reload(false);
      },
      error: function() {
        _alert({ message: gettext('Your edits failed to save. Please try again.') }, 'error');
      }
    });

    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel-details').on('click', (event) => {
    if (grant_description) {
      grant_description.enable(false);
      grant_description.setContents(_text);
    }
    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');
    $('.grant__progress').removeClass('hidden');

    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel_grant').on('click', function(e) {

    $('.modal-cancel-grants').on('click', function(e) {
      let contract_address = $('#contract_address').val();
      let grant_cancel_tx_id;
      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, contract_address);

      web3.eth.getAccounts(function(err, accounts) {
        deployedSubscription.methods.endContract()
          .send({
            from: accounts[0],
            gas: 3000000,
            gasPrice: web3.utils.toHex($('#gasPrice').val() * Math.pow(10, 9))
          }).on('transactionHash', function(transactionHash) {
            grant_cancel_tx_id = $('#grant_cancel_tx_id').val();
            const linkURL = get_etherscan_url(transactionHash);

            document.issueURL = linkURL;
            $('#transaction_url').attr('href', linkURL);
            $('.modal .close').trigger('click');
            enableWaitState('#grants-details');
          })
          .on('confirmation', function(confirmationNumber, receipt) {
            $.ajax({
              type: 'post',
              url: '',
              data: {
                'contract_address': contract_address,
                'grant_cancel_tx_id': grant_cancel_tx_id
              },
              success: function(json) {
                window.location.reload(false);
              },
              error: function() {
                _alert({ message: gettext('Canceling your grant failed to save. Please try again.') }, 'error');
              }
            });
          });
      });
    });
  });

  $('#contract_owner_button').on('click', function(e) {
    let contract_owner_address = $('#contract_owner_address').val();
    let contract_address = $('#contract_address').val();
    let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, contract_address);

    web3.eth.getAccounts(function(err, accounts) {
      deployedSubscription.methods.changeOwnership(
        contract_owner_address
      ).send({
        from: accounts[0],
        gasPrice: 8000000000
      }).on('transactionHash', function(transactionHash) {
        const linkURL = get_etherscan_url(transactionHash);

        document.issueURL = linkURL;
        $('#transaction_url').attr('href', linkURL);
        $('.modal .close').trigger('click');
        enableWaitState('#grants-details');
      }).on('confirmation', function(confirmationNumber, receipt) {
        $.ajax({
          type: 'post',
          url: '',
          data: {
            'contract_owner_address': contract_owner_address
          },
          success: function(json) {
            window.location.reload(false);
          },
          error: function() {
            _alert({ message: gettext('Changing the contract owner address failed to save. Please try again.') }, 'error');
          }
        });
      });
    });
  });

});

const makeEditable = (input) => {
  $(input).addClass('editable');
  $(input).prop('readonly', false);
  $(input).prop('disabled', false);
};

const disableEdit = (input) => {
  $(input).removeClass('editable');
  $(input).prop('readonly', true);
  $(input).prop('disabled', true);

  $('#contract_owner_button').addClass('hidden');
};

const copyDuplicateDetails = () => {
  let obj = {};

  editableFields.forEach(field => {
    obj[field] = $(field).val() ? $(field).val() : $(field).last().text();
  });

  $('#save-details').on('click', () => {
    if (
      obj['#grant-admin'] &&
      obj['#grant-admin'] != $('#grant-admin option').last().text()
    ) {
      localStorage['request_change'] = 'R';
    }
  });

  $('#cancel-details').on('click', () => {
    editableFields.forEach(field => {
      if (field == '#grant-admin')
        $(field).val([obj[field]]).trigger('change');
      else if (field == '#grant-members')
        $(field).val(obj[field]).trigger('change');
      else
        $(field).val(obj[field]);
    });
  });
};

$(document).ready(() => {
  $('#grant-profile-tabs button').click(function() {
    document.location = $(this).attr('href');
  });
});