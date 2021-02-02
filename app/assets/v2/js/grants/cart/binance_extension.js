const contributeWithBinanceExtension = async (grant, vm) => {
  const amount = grant.grant_donation_amount;
  const token_name = grant.grant_donation_currency;
  const to_address = grant.binance_payout_address;

  try {
    const from_address = await binance_utils.getSelectedAccount();
  } catch (error) {
    _alert({ message: `Please ensure your Binance Chain Extension wallet is installed and enabled`}, 'error');
    return;
  }

  if (!token_name) {
    token_name = 'BNB';
  }

  if (token_name === 'BNB') {
    const account_balance = await binance_utils.getAddressBalance(from_address);

    if (Number(account_balance) < amount) {
      _alert({ message: `Account needs to have more than ${amount} BNB for payout` }, 'error');
      return;
    }
  } else if (token_name === 'BUSD') {
    const busd_contract_address = '0xe9e7cea3dedca5984780bafc599bd69add087d56'

    const account_balance = await binance_utils.getAddressTokenBalance(from_address, busd_contract_address);

    if (Number(account_balance) < amount ) {
      _alert({ message: `Account needs to have more than ${amount} BUSD for payout` }, 'error');
      return;
    }
  }

  binance_utils.transferViaExtension(
    amount * 10 ** vm.decimals,
    to_address,
    from_address,
    token_name
  ).then(txn => {
    if (txn) {
      callback(null, from_address, txn);
    } else {
      callback('error in signing transaction');
    }
  }).catch(err => {
    callback(err);
  });

  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'error');
      console.log(error);
    } else {

      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'BINANCE',
          'comment': grant.grant_comments,
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlGrant = `v1/api/contribute`;

      fetchData(apiUrlGrant, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);

          vm.updatePaymentStatus(grant.grant_id, 'done', txn);

        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to make contribute to grant. Please try again later', 'error');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function (error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to make contribute to grant. Please try again later', 'error');
        console.log(error);
      });
    }
  }
};