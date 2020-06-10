/* eslint-disable no-console */

let description = new Quill('#input-description', {
  theme: 'snow'
});

$(document).ready(function() {

  $('.select2-selection__choice').removeAttr('title');

  if (web3 && web3.eth) {
    web3.eth.net.isListening((error, connectionStatus) => {
      if (connectionStatus)
        init();
      document.init = true;
    });
  }
  // fix for triage bug https://gitcoincore.slack.com/archives/CAXQ7PT60/p1551220641086800
  setTimeout(function() {
    if (!document.init) {
      show_error_banner();
    }
  }, 1000);
});

function saveGrant(grantData, isFinal) {
  let csrftoken = $("#create-grant input[name='csrfmiddlewaretoken']").val();

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
        }
      }
    },
    error: () => {
      console.error('Grant failed to save');
      _alert({ message: gettext('Your grant failed to save. Please try again.') }, 'error');
    }
  });
}



const init = () => {
  if (localStorage['grants_quickstart_disable'] !== 'true') {
    window.location = document.location.origin + '/grants/quickstart';
  }

  web3.eth.getAccounts(function(err, accounts) {
    $('#input-admin_address').val(accounts[0]);
    $('#contract_owner_address').val(accounts[0]);
  });

  $('#js-token').append("<option value='0x0000000000000000000000000000000000000000'>Any Token");

  userSearch('.team_members', false, undefined, false, false, true);

  addGrantLogo();

  $('.js-select2, #frequency_unit').each(function() {
    $(this).select2();
  });

  $('#input-admin_address').on('change', function() {
    $('.alert').remove();
    const validator = $('#create-grant').validate();
    let address = $(this).val();

    if (isNaN(parseInt(address))) {
      web3.eth.ens.getAddress(address).then(function(result) {
        $('#input-admin_address').val(result);
        return result;
      }).catch(function() {
        validator.showErrors({
          'admin_address': 'Please check your address!'
        });
        return _alert({ message: gettext('Please check your address and try again.') }, 'error');
      });
    }
  });

  $('#create-grant').submit(function(e) {
    e.preventDefault();
  }).validate({
    submitHandler: function(form) {
      let data = {};

      var recipient_addr = $('#input-admin_address').val();
      var msg = 'You have specified ' + recipient_addr + ' as the grant funding recipient address. Please TRIPLE CHECK that this is the correct address to receive funds for contributions to this grant.  If access to this address is lost, you will not be able to access funds from contributors to this grant.';

      if (!confirm(msg)) {
        return;
      }

      $(form).find(':input:disabled').removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      $('#token_symbol').val($('#js-token option:selected').text());
      $('#token_address').val($('#js-token option:selected').val());

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
      formData.append('admin_address', $('#input-admin_address').val());
      formData.append('contract_owner_address', $('#contract_owner_address').val());
      formData.append('token_address', $('#token_address').val());
      formData.append('token_symbol', $('#token_symbol').val());
      formData.append('contract_version', $('#contract_version').val());
      formData.append('transaction_hash', $('#transaction_hash').val());
      formData.append('network', $('#network').val());
      formData.append('team_members[]', $('#input-team_members').val());
      formData.append('categories[]', $('#input-categories').val());
      formData.append('grant_type', $('#input-grant_type').val().toLowerCase());
      formData.append('contract_address', '0x0');
      formData.append('transaction_hash', '0x0');

      saveGrant(formData, true);

      return false;
    }
  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      let option = document.createElement('option');

      option.text = ele.name;
      option.value = ele.addr;

      $('#js-token').append($('<option>', {
        value: ele.addr,
        text: ele.name
      }));
    });

    $('#js-token').select2();
    $("#js-token option[value='0x0000000000000000000000000000000000000000']").remove();
    $('#js-token').append("<option value='0x0000000000000000000000000000000000000000' selected='selected'>Any Token");
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
