const contributeWithHarmonyExtension = async(grant, vm, modal) => {

  const amount = grant.grant_donation_amount;
  const to_address = grant.harmony_payout_address;

  // step 1: init harmony
  let hmy = harmony_utils.initHarmony();

  // step 2: init extension and ensure right from_address is connected
  let harmonyExt = await harmony_utils.initHarmonyExtension('test');
  const from_address = await harmony_utils.loginHarmonyExtension(harmonyExt);

  // step 3: check balance
  const account_balance = await harmony_utils.getAddressBalance(hmy, from_address);

  if (account_balance < amount) {
    _alert({ message: `Account needs to have more than ${amount} ONE in shard 0 for payout`}, 'error');
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
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'error');
      console.log(error);
    } else {

      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'HARMONY',
          'comment': grant.grant_comments,
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = `v1/api/contribute`;

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);

          // TODO: Show success message in modal 
          // TODO: remove grant from cart 
          // vm.removeGrantFromCart(grant.grant_id)

        } else {
          _alert('Unable to make contribute to grant. Please try again later', 'error');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        _alert('Unable to make contribute to grant. Please try again later', 'error');
        console.log(error);
      });
    }
  }
};