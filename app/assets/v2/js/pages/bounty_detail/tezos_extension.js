const payWithTezosExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  let selectedAddress;

  const client = new beacon.DAppClient({ name: 'Gitcoin <> Tezos' });
  const activeAccount = await client.getActiveAccount();

  console.log(activeAccount);

  if (activeAccount) {
    console.log('Already connected:', activeAccount.address);
    selectedAddress = activeAccount.address;
  } else {
    try {
      const permissions = await client.requestPermissions();

      console.log('New connection:', permissions.address);
      selectedAddress = permissions.address;
    } catch (e) {
      console.log(e);
    }
  }

  let txArgs;
  
  // if (token_name == 'XTZ') {
  
  //   // balanceInWei = await rskClient.eth.getBalance(ethereum.selectedAddress);
  
  //   // rbtcBalance = rskClient.utils.fromWei(balanceInWei, 'ether');
  
  //   // if (Number(rbtcBalance) < amount) {
  //   //   _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'danger');
  //   //   return;
  //   // }
  
  // } else {

  // }

  const response = await client.requestOperation({
    operationDetails: [
      {
        kind: beacon.TezosOperationType.TRANSACTION,
        destination: selectedAddress, // Send to ourselves - should be to_address
        amount: '1' // Amount in mutez, the smallest unit in Tezos - should be amount
      }
    ]
  });
    
  console.log('Operation Hash: ', response.transactionHash);

  const explorerLink = await client.blockExplorer.getTransactionLink(
    response.transactionHash,
    network
  );
    
  console.log('Block Explorer:', explorerLink);
  
  callback(null, selectedAddress, response.transactionHash);
  
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
  