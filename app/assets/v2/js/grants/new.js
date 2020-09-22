/* eslint-disable no-console */

let description = new Quill('#input-description', {
  theme: 'snow'
});

function changeTokens() {
  $("#js-token option[value='0x0000000000000000000000000000000000000000']").text('Any Token');
  $('#js-token').select2();
}

window.addEventListener('tokensReady', function(e) {
  changeTokens();
}, false);
needWalletConnection();


const init = () => {
  /*
  KO - commenting out during grants deploy, double check with Octavio
  if (!provider) {
    return onConnect();
  }
  */

  if (localStorage['grants_quickstart_disable'] !== 'true' && window.location.pathname.includes('matic') == false) {
    window.location = document.location.origin + '/grants/quickstart';
  }

  $('#input-admin_address').val(selectedAccount);
  $('#contract_owner_address').val(selectedAccount);
  userSearch('.team_members', false, undefined, false, false, true);

  addGrantLogo();

  $('.js-select2, #frequency_unit').each(function() {
    $(this).select2();
  });

  jQuery.validator.setDefaults({
    ignore: ":hidden, [contenteditable='true']:not([name])"
  });

  $('#input-admin_address').on('input', function() {
    $('.alert').remove();
    const address = $(this).val();
    const isNumber = !isNaN(parseInt(address));

    if (isNumber) {
      return;
    }

    const isENSName = address.trim().endsWith('.eth');

    if (!isENSName) {
      return;
    }

    web3.eth.ens.getAddress(address).then(function(result) {
      $('#input-admin_address').val(result);
      return result;
    }).catch(function(_error) {
      _alert({ message: gettext('Please check your address and try again.') }, 'error');
      return false;
    });
  });

  $('#input-admin_address').on('change', function() {
    $('.alert').remove();
    const validator = $('#create-grant').validate();
    let address = $(this).val();

    if (isNaN(parseInt(address))) {
      web3.eth.ens.getAddress(address).then(function(result) {
        $('#input-admin_address').val(result);
        return result;
      }).catch(function(_error) {
        validator.showErrors({
          'admin_address': 'Please check your address!'
        });
        _alert({ message: gettext('Please check your address and try again.') }, 'error');
        return false;
      });
    }
  });

  $('#create-grant').submit(function(e) {
    e.preventDefault();
  }).validate({
    submitHandler: function(form) {
      let data = {};

      var recipient_addr = $('#input-admin_address').val();

      if (isNaN(parseInt(recipient_addr))) {
        alert(`The address ${recipient_addr} is not valid`);
        return false;
      }
      var msg = 'You have specified ' + recipient_addr + ' as the grant funding recipient address. Please TRIPLE CHECK that this is the correct address to receive funds for contributions to this grant.  If access to this address is lost, you will not be able to access funds from contributors to this grant.';

      if (!confirm(msg)) {
        return false;
      }

      $(form).find(':input:disabled').removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      if ($('#token_address').length) {
        $('#token_symbol').val($('#js-token option:selected').text());
        $('#token_address').val($('#js-token option:selected').val());
      }

      if (document.web3network) {
        $('#network').val(document.web3network);
      }

      // These args are baseline requirements for the contract set by the sender. Will set most to zero to abstract complexity from user.
      let args;

      if ($('#contract_version').val() == 1) {
        args = [
          // admin_address
          web3.utils.toChecksumAddress(data.admin_address),
          // required token
          web3.utils.toChecksumAddress(data.denomination),
          // required tokenAmount
          web3.utils.toTwosComplement(0),
          // data.frequency
          web3.utils.toTwosComplement(0),
          // data.gas_price
          web3.utils.toTwosComplement(0),
          // contract version
          web3.utils.toTwosComplement(1),
          // trusted relayer
          web3.utils.toChecksumAddress(data.trusted_relayer)
        ];
      }

      let formData = new FormData();
      let file = $('#img-project')[0].files[0];

      formData.append('input_image', file);
      formData.append('title', $('#input_title').val());
      formData.append('handle1', $('#input-handle1').val());
      formData.append('handle2', $('#input-handle2').val());
      formData.append('description', description.getText());
      formData.append('description_rich', JSON.stringify(description.getContents()));
      formData.append('reference_url', $('#input-url').val());
      formData.append('github_project_url', $('#github_project_url').val());
      formData.append('admin_address', $('#input-admin_address').val());
      formData.append('contract_owner_address', $('#contract_owner_address').val());
      if ($('#token_address').length) {
        formData.append('token_address', $('#token_address').val());
        formData.append('token_symbol', $('#token_symbol').val());
      } else {
        formData.append('token_address', '0x0000000000000000000000000000000000000000');
        formData.append('token_symbol', 'Any Token');
      }
      formData.append('contract_version', $('#contract_version').val());
      formData.append('transaction_hash', $('#transaction_hash').val());
      if ($('#network').val()) {
        formData.append('network', $('#network').val());
      } else {
        formData.append('network', 'mainnet');
      }
      formData.append('team_members[]', $('#input-team_members').val());
      formData.append('categories[]', $('#input-categories').val());
      formData.append('grant_type', $('#input-grant_type').val().toLowerCase());
      formData.append('contract_address', '0x0');
      formData.append('transaction_hash', '0x0');

      saveGrant(formData, true);

      return false;
    }
  });

  grantCategoriesSelection('.categories', '/grants/categories?type=tech');

  $('#input-grant_type').on('change', function() {
    $('.categories').val(null);
    const type = this.value && this.value.toLowerCase();

    grantCategoriesSelection('.categories', `/grants/categories?type=${type}`);
  });

  $('.select2-selection__rendered').hover(function() {
    $(this).removeAttr('title');
  });
};

$(document).ready(function() {

  $('.select2-selection__choice').removeAttr('title');
  init();
  changeTokens();
});

function saveGrant(grantData, isFinal) {
  let csrftoken = $("#create-grant input[name='csrfmiddlewaretoken']").val();

  $('#new_button').attr('disabled', 'disabled');

  $.ajax({
    type: 'post',
    url: '/grants/new',
    processData: false,
    contentType: false,
    data: grantData,
    headers: {'X-CSRFToken': csrftoken},
    success: json => {
      if (isFinal) {
        if (json.url) {
          document.suppress_loading_leave_code = true;
          window.location = json.url;
        } else {
          console.error('Grant failed to save');
          $('#new_button').attr('disabled', false);
        }
      }
    },
    error: () => {
      console.error('Grant failed to save');
      _alert({ message: gettext('Your grant failed to save. Please try again.') }, 'error');
      $('#new_button').attr('disabled', false);
    }
  });
}


$('#new_button').on('click', function(e) {
  if (!provider && $('#token_address').length != 0) {
    e.preventDefault();
    return onConnect().then(() => init());
  }
});
