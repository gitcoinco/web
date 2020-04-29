/* eslint-disable no-console */
window.onload = function() {

  $('.rating input:radio').attr('checked', false);

  $('.rating input').click(function() {
    $('.rating span').removeClass('checked');
    $(this).parent().addClass('checked');
  });

  if (is_bounties_network) {
    fetchFromWeb3Wallet();
  }

  if (typeof localStorage['githubUsername'] != 'undefined') {
    if (!$('input[name=githubUsername]').val()) {
      $('input[name=githubUsername]').val(localStorage['githubUsername']);
    }
  }
  if (typeof localStorage['notificationEmail'] != 'undefined') {
    $('input[name=notificationEmail]').val(localStorage['notificationEmail']);
  }
  if (getParam('source')) {
    $('input[name=issueURL]').val(getParam('source'));
  }

  $('#submitBounty').validate({
    submitHandler: function(form) {

      let data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      if (is_bounties_network) {
        ethFulfillBounty(data);
      } else {
        fulfillBounty(data);
      }
    }
  });
};

const fetchFromWeb3Wallet = () => {
  web3.eth.getAccounts(function(_, accounts) {
    $('#payoutAddress').val(accounts[0]);
    $('#payoutAddress').attr('disabled', true);
  });
}
