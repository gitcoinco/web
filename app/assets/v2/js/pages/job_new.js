$(function() {
  $('#new_job_form').submit(function(event) {
    event.preventDefault();
    purchaseJobPosting();
  });
});

function purchaseJobPosting(option, value, target) {
  _alert('You will now be prompted via Metamask to purchase.', 'info');
  var cost_wei = web3.toWei(0.1);

  to_address = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
  web3.eth.sendTransaction(
    {
      from: web3.eth.coinbase,
      to: to_address,
      value: cost_wei
    },
    function(error, result) {
      if (error) {
        _alert('There was an error.', 'error');
        return;
      }
      showBusyOverlay();
      _alert('Waiting for tx to mine...', 'info');
      callFunctionWhenTransactionMined(result, function() {
        $('#id_txid').val(result);

        $.post('/jobs/new/', $('#new_job_form').serialize()).then(function() {
          hideBusyOverlay();
          _alert('Success ✅ Loading your purchase now.', 'success');
          setTimeout(function() {
            location.reload();
          });
        });
      });
    }
  );
  return;
}
