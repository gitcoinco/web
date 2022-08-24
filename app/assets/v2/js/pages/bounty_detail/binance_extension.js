const payWithBinanceExtension = (fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;
  const from_address = vm.bounty.bounty_owner_address;

  binance_utils.transferViaExtension(
    amount * 10 ** vm.decimals,
    to_address,
    from_address,
    vm.bounty.token_name
  ).then(txn => {
    callback(null, from_address, txn);
  }).catch(err => {
    callback(err);
  });

  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty: ' + error) }, 'danger');
      console.log(error);
    } else {

      const payload = {
        payout_type: 'binance_ext',
        tenant: 'BINANCE',
        amount: amount,
        token_name: token_name,
        funder_address: from_address,
        payout_tx_id: txn
      };

      modal.closeModal();
      const apiUrlBounty = `/api/v1/bounty/payout/${fulfillment_id}`;

      fetchData(apiUrlBounty, 'POST', payload).then(response => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);

          vm.fetchBounty();
          _alert('Payment Successful');

        } else {
          _alert('Unable to make payout bounty. Please try again later', 'danger');
          console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        _alert('Unable to make payout bounty. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
