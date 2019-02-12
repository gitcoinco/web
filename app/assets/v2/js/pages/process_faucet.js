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

  $('#submitFaucet').on('click', function(e) {
    e.preventDefault();
    $('.js-submit').attr('disabled', 'disabled');
    $('#loadingImg').show();
    var fundingAccount = web3.eth.coinbase;
    var destinationAccount = $('#destinationAccount').val();
    var faucetAmount = $('#faucetAmount').val();

    decimals = 6;
    faucetAmount = Math.round(faucetAmount * 10 ** decimals) / 10 ** decimals;
    console.log(fundingAccount, 'from:to', destinationAccount);
    web3.eth.sendTransaction({
      from: fundingAccount,
      to: destinationAccount,
      value: web3.toWei(parseFloat(faucetAmount), 'ether'),
      gasPrice: web3.toHex(document.gas_price * Math.pow(10, 9))
    }, post_receipt);
  });
});
