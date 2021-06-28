const payWithTezosExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  let selectedAddress;
  
  const Tezos = new taquito.TezosToolkit('https://mainnet-tezos.giganode.io');
  const wallet = new taquitoBeaconWallet.BeaconWallet({ name: 'Gitcoin' });
  
  Tezos.setWalletProvider(wallet);

  const activeAccount = await wallet.client.getActiveAccount();
  
  if (activeAccount) {
    console.log('Already connected:', activeAccount.address);
    selectedAddress = activeAccount.address;
  } else {
    try {
      await wallet.requestPermissions();
      selectedAddress = await wallet.getPKH();
      console.log('New connection:', selectedAddress);
    } catch (e) {
      console.log(e);
    }
  }
        
  if (token_name == 'XTZ') {
    try {
      const txHash = await wallet.sendOperations([
        {
          kind: beacon.TezosOperationType.TRANSACTION,
          destination: to_address,
          amount: amount * 10 ** vm.decimals
        }
      ]);

      callback(null, selectedAddress, txHash);
    } catch (e) {
      modal.closeModal();
      _alert({ message: `${e.title} - ${e.description}` }, 'danger');
      console.log(e);
    }
  }
  
  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to: ' + error) }, 'danger');
      console.log(error);
    } else {
      
      const payload = {
        payout_type: 'tezos_ext',
        tenant: 'TEZOS',
        amount: amount,
        token_name: token_name,
        funder_address: from_address,
        payout_tx_id: txn
      };
      
      modal.closeModal();
      const apiUrlBounty = `/api/v1/bounty/payout/${fulfillment_id}`;
      
      fetchData(apiUrlBounty, 'POST', payload).then(response => {
        if (200 <= response.status && response.status <= 204) {
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
        