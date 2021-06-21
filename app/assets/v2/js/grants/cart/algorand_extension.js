const contributeWithAlgorandExtension = async(grant, vm, modal) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const to_address = grant.rsk_payout_address;
  const token = vm.getTokenByName(token_name);

  // TODO: FIGURE OUT from_address

  // const NETWORK = 'TestNet';
  const NETWORK = 'MainNet';

  // 1. check if AlgoSigner is available
  if (!AlgoSigner) {
    _alert({ message: 'Please download or enable AlgoSigner extension' }, 'danger');
    modal.closeModal();
    return;
  }

  try {
    AlgoSigner.connect().then(async() => {
      // step2: get connected accounts
      const accounts = await AlgoSigner.accounts({ ledger: NETWORK });

      let is_account_present = false;

      accounts.map(account=> {
        if (account.address == from_address)
          is_account_present = true;
      });
      
      if (!is_account_present) {
        _alert({ message: `Unable to access address ${from_address} in wallet` }, 'danger');
        modal.closeModal();
        return;
      }
      
      // step3: check if enough balance is present
      const balance = await AlgoSigner.algod({
        ledger: NETWORK,
        path: `/v2/accounts/${from_address}`
      });

      if (
        token_name == 'ALGO' &&
        Number(balance.amount) <= amount * 10 ** token.decimals
      ) {
        // ALGO token
        _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
        modal.closeModal();
        return;

      }
      // ALGO assets
      let is_asset_present = false;

      if (balance.assets && balance.assets.length > 0) {
        balance.assets.map(asset => {
          if (asset['asset-id'] == asset_index)
            is_asset_present = true;
        });
      }

      if (is_asset_present) {
        _alert({ message: `Asset ${token_name} is not present in ${from_address}` }, 'danger');
        modal.closeModal();
        return;
      }

      let has_enough_asset_balance = false;

      balance.assets.map(asset => {
        if (asset['asset-id'] == asset_index && asset['amount'] <= amount * 10 ** token.decimals)
          has_enough_asset_balance = true;
      });

      if (has_enough_asset_balance) {
        _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
        modal.closeModal();
        return;
      }
      

      // step4: get txnParams
      const txParams = await AlgoSigner.algod({
        ledger: NETWORK,
        path: '/v2/transactions/params'
      });

      let txn;
      // step5: sign transaction

      if (token_name == 'ALGO') {
        // ALGO token
        txn = {
          from: from_address,
          to: to_address,
          fee: txParams['fee'],
          type: 'pay',
          amount: amount * 10 ** token.decimals,
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash'],
          note: 'contributing to gitcoin grant'
        };
      } else {
        // ALGO assets
        txn = {
          from: from_address,
          to: to_address,
          assetIndex: Number(asset_index.addr),
          note: 'contributing to gitcoin grant',
          amount: amount * 10 ** token.decimals,
          type: 'axfer',
          fee: txParams['min-fee'],
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash']
        };
      }

      AlgoSigner.sign(txn).then(signedTx => {

        // step6: broadcast txn
        AlgoSigner.send({
          ledger: NETWORK,
          tx: signedTx.blob
        })
          .then(tx => {
            callback(null, from_address, tx.txId);
          })
          .catch((e) => {
            console.log(e);
            _alert({ message: 'Unable to broadcast txn. Please try again' }, 'danger');
            modal.closeModal();
            return;
          });

      }).catch(e => {
        console.log(e);
        _alert({ message: 'Unable to sign txn. Please try again' }, 'danger');
        modal.closeModal();
        return;
      });

    }).catch(e => {
      console.log(e);
      _alert({ message: 'Please allow Gitcoin to connect to AlgoSigner extension' }, 'danger');
      modal.closeModal();
      return;
    });
  } catch (e) {
    modal.closeModal();
    _alert({ message: 'Unable to make contribution to grant. Please try again later.' }, 'error');
    console.log(error);
    return;
  }
  

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
          'tenant': 'ALGORAND',
          'comment': grant.grant_comments,
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
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
          _alert('Unable to make contribute to grant. Please try again later', 'danger');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to make contribute to grant. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
