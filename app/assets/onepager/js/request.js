$(document).ready(function() {

  $('#network').change(function(e) {
    if ($(this).val() !== 'ETH') {
      $('#token').prop('disabled', 'disabled');
      $('#token').val('');
    } else {
      $('#token').prop('disabled', false);
    }
  });
  $('#request').on('click', function(e) {
    e.preventDefault();
    if ($(this).hasClass('disabled'))
      return false;

    if (!$('#tos').is(':checked')) {
      _alert('Please accept the terms and conditions before submit.', 'warning');
      return false;
    }

    // get form data
    const username = $('.username-search').select2('data')[0] ? $('.username-search').select2('data')[0].text : '';
    const amount = parseFloat($('#amount').val());
    const network = $('#network').val();
    const address = $('#address').val();
    const comments = $('#comments').val();

    if (!document.contxt['github_handle']) {
      _alert('You must be logged in to use this form', 'warning');
      return false;
    }

    if (!provider) {
      return onConnect().then(() => {
        return false;
      });
    }

    if (!username || !amount || !address) {
      _alert('Please fill all the fields.', 'warning');
      return false;
    }

    if (username == document.contxt['github_handle']) {
      _alert('You cannot request money from yourself.', 'warning');
      return false;
    }
    if (!comments || comments.length < 5) {
      _alert('Please leave a comment describing why this user should send you money.', 'warning');
      return false;
    }
    loading_button($(this));

    const tokenAddress = (
      ($('#token').val() == '0x0') ?
        '0x0000000000000000000000000000000000000000'
        : $('#token').val());


    // derived info
    const isSendingETH = (tokenAddress == '0x0' || tokenAddress == '0x0000000000000000000000000000000000000000');
    const tokenDetails = tokenAddressToDetails(tokenAddress);
    let tokenName;

    if (network == 'ETH' == !isSendingETH) {
      tokenName = tokenDetails.name;
    } else {
      tokenName = 'ETH';
    }

    if (!username) {
      _alert('Please enter a recipient', 'danger');
      return;
    }

    const success_callback = function() {
      unloading_button($('#request'));
    };
    const failure_callback = function() {
      unloading_button($('#request'));
    };

    return requestFunds(username, amount, comments, tokenAddress, tokenName, network, address, success_callback, failure_callback);

  });

});

function requestFunds(username, amount, comments, tokenAddress, tokenName, network, address, success_callback, failure_callback) {
  if (username.indexOf('@') == -1) {
    username = '@' + username;
  }

  if (!isNumeric(amount) || amount == 0) {
    _alert({ message: gettext('You must enter the amount!') }, 'warning');
    failure_callback();
    return;
  }
  if (username == '') {
    _alert({ message: gettext('You must enter a username.') }, 'warning');
    failure_callback();
    return;
  }

  const csrfmiddlewaretoken = $('[name=csrfmiddlewaretoken]').val();
  const url = '/requestmoney';
  const formData = new FormData();

  formData.append('username', username);
  formData.append('amount', amount);
  formData.append('tokenName', tokenName);
  formData.append('comments', comments);
  formData.append('tokenAddress', tokenAddress);
  formData.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
  formData.append('network', network);
  formData.append('address', address);
  fetch(url, {
    method: 'POST',
    body: formData
  }).then(function(json) {
    _alert('The funder has been notified', 'success');
    success_callback();
  }).catch(function(error) {
    _alert('Something goes wrong, try later.', 'danger');
    failure_callback();
  });
}

window.addEventListener('load', async() => {
  if (!provider && !web3Modal.cachedProvider || provider === 'undefined') {
    onConnect().then(() => {
      $('#address').val(selectedAccount);
    });
  } else {
    web3Modal.on('connect', async(data) => {
      $('#address').val(data.selectedAddress);
    });
  }
});
