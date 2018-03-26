$(document).ready(function() {
  var post_receipt = function(err, res) {
    $('#loadingImg').hide();
    $('.js-submit').removeAttr('disabled');
    if (err != null) {
      $('#failureReason').html(err.message);
      $('#errResponse').show();
      return;
    }
    $('#admin_faucet_form').submit();
  };

  $('#submitFaucet').click(function(e) {
    e.preventDefault();
    $('.js-submit').attr('disabled', 'disabled');
    $('#loadingImg').show();
    var fundingAccount = web3.eth.coinbase;
    var destinationAccount = $('#destinationAccount').val();
    var faucetAmount = $('#faucetAmount').val();

    web3.eth.sendTransaction({
      from: fundingAccount,
      to: destinationAccount,
      value: web3.toWei(faucetAmount, 'ether')
    }, post_receipt);
  });
});
