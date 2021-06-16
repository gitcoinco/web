const payWithTezosExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  let selectedAddress;
  
  // const Tezos = new taquito.TezosToolkit("https://mainnet-tezos.giganode.io");
  const Tezos = new taquito.TezosToolkit('https://edonet-tezos.giganode.io');
  const wallet = new taquitoBeaconWallet.BeaconWallet({
    name: 'Gitcoin',
    preferredNetwork: beacon.NetworkType.EDONET
  }); // Takes the same arguments as the DAppClient constructor
  
  Tezos.setWalletProvider(wallet);
  
  await wallet.clearActiveAccount();
  const activeAccount = await wallet.client.getActiveAccount();
  
  if (activeAccount) {
    console.log('Already connected:', activeAccount.address);
    selectedAddress = activeAccount.address;
  } else {
    try {
      await wallet.requestPermissions(
        {
          network: {
            type: beacon.NetworkType.EDONET,
            rpcUrl: 'https://edonet-tezos.giganode.io'
          }
        }
      );
      selectedAddress = await wallet.getPKH();
      console.log('New connection:', selectedAddress);
    } catch (e) {
      console.log(e);
    }
  }
  
  // if (token_name == 'XTZ') {
    
  //   // balanceInWei = await rskClient.eth.getBalance(ethereum.selectedAddress);
    
  //   // rbtcBalance = rskClient.utils.fromWei(balanceInWei, 'ether');
    
  //   // if (Number(rbtcBalance) < amount) {
  //   //   _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'danger');
  //   //   return;
  //   // }
      
  // } else {
        
  // }
        
  try {
    console.log(Tezos);
    let balanceInMutez = await Tezos.tz.getBalance(selectedAddress);
    
    console.log(balanceInMutez);
    
    const txHash = await wallet.sendOperations([
      {
        kind: beacon.TezosOperationType.TRANSACTION,
        destination: selectedAddress, // Send to ourselves - should be to_address
        amount: amount * 10 ** vm.decimals
      }
    ]);
    
    console.log('Operation Hash: ', txHash);
    
    const explorerLink = await wallet.client.blockExplorer.getTransactionLink(
      txHash,
      network
    );

    console.log('Block Explorer:', explorerLink);

    callback(null, selectedAddress, txHash);
  } catch (e) {
    modal.closeModal();
    _alert({ message: `${e.title} - ${e.description}` }, 'danger');
    console.log(e);
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
        