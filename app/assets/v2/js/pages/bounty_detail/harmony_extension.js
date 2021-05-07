const payWithHarmonyExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;
  const from_address = vm.bounty.bounty_owner_address;

  // step 1: init harmony
  let hmy = harmony_utils.initHarmony();

  // step 2: check balance
  const account_balance = await harmony_utils.getAddressBalance(hmy, from_address);

  if (account_balance < amount) {
    _alert({ message: `Account needs to have more than ${amount} ONE in shard 0 for payout`}, 'danger');
    return;
  }

  // step 3: init extension and ensure right from_address is connected
  let harmonyExt = await harmony_utils.initHarmonyExtension();
  let address = await harmony_utils.loginHarmonyExtension(harmonyExt);

  if (address != from_address) {
    _alert({ message: `Connect address ${from_address} to payout`}, 'danger');
    harmony_utils.logoutHarmonyExtension(harmonyExt);
    return;
  }

  // step 4: payout
  harmony_utils.transfer(
    hmy,
    harmonyExt,
    from_address,
    to_address,
    amount
  ).then(txn => {
    if (txn) {
      callback(null, from_address, txn);
    } else {
      callback('error in signing transaction');
    }
  }).catch(err => callback(err));


  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to ' + error) }, 'danger');
      console.log(error);
    } else {

      const payload = {
        payout_type: 'harmony_ext',
        tenant: 'HARMONY',
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
          _alert('Payment Successful', 'success');

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
