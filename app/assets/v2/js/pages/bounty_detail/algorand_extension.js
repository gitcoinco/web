const payWithAlgorandExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;
  const from_address = (vm.bounty.bounty_owner_address).toUpperCase();
  const asset_index = tokenNameToDetails('mainnet', token_name);
  // const NETWORK = 'TestNet';
  const NETWORK = 'MainNet';

  try {

    // step1: init connection
    if (!AlgoSigner) {
      _alert({ message: 'Please download or enable AlgoSigner extension' }, 'danger');
      modal.closeModal();
      return;
    }

    // const connect = await AlgoSigner.connect();
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
        balance.amount <= amount * 10 ** vm.decimals
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
        if (asset['asset-id'] == asset_index && asset['amount'] <= amount * 10 ** vm.decimals)
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
          amount: amount * 10 ** vm.decimals,
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash'],
          note: 'paying out gitcoin bounty'
        };
      } else {
        // ALGO assets
        txn = {
          from: from_address,
          to: to_address,
          assetIndex: Number(asset_index.addr),
          note: 'paying out gitcoin bounty',
          amount: amount * 10 ** vm.decimals,
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
    _alert({ message: 'Error paying out using Algorand ' }, 'error');
    return;
  }

  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to: ' + error) }, 'danger');
      console.log(error);
    } else {

      const payload = {
        payout_type: 'algorand_ext',
        tenant: 'ALGORAND',
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