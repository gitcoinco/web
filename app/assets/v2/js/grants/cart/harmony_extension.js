const contributeWithHarmonyExtension = async(grant, vm, modal) => {

  if (!harmony_utils.isOnewalletInstalled()) {
    _alert({ message: 'Please ensure your Harmony One wallet is installed and unlocked'}, 'danger');
    return;
  }

  const amount = grant.grant_donation_amount;
  const to_address = grant.harmony_payout_address;

  // step 1: init harmony
  let hmy = harmony_utils.initHarmony();

  // step 2: init extension
  let harmonyExt = await harmony_utils.initHarmonyExtension();

  // step 3: check balance
  const from_address = await harmony_utils.loginHarmonyExtension(harmonyExt);
  const account_balance = await harmony_utils.getAddressBalance(hmy, from_address);

  if (account_balance < amount) {
    _alert({ message: `Account needs to have more than ${amount} ONE in shard 0 for payout`}, 'danger');
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
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'danger');
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

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        console.log(response);
        console.log(payload);
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
          MauticEvent.createEvent({
            'alias': 'products',
            'data': [
              {
                'name': 'product',
                'attributes': {
                  'product': 'grants',
                  'persona': 'grants-contributor',
                  'action': 'contribute'
                }
              }
            ]
          });

          vm.updatePaymentStatus(grant.grant_id, 'done', txn);

        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to contribute to grant. Please try again later', 'danger');
          harmony_utils.logoutHarmonyExtension(harmonyExt);
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to contribute to grant. Please try again later', 'danger');
        harmony_utils.logoutHarmonyExtension(harmonyExt);
        console.log(error);
      });
    }
  }
};
