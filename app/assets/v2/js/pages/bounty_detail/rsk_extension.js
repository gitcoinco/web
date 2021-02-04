const payWithRSKExtension = async (fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  // 1. init rsk provider
  const rskHost = "https://public-node.testnet.rsk.co"
  const rskClient = new Web3();
  rskClient.setProvider(
    new rskClient.providers.HttpProvider(rskHost)
  );

  // TODO: Prompt user to unlock wallet if ethereum.selectedAddress is not present


  // 2. construct + sign txn via nifty
  if (token_name == 'R-BTC') {
    const tx_args = {
      to: to_address.toLowerCase(),
      from: ethereum.selectedAddress,
      value: rskClient.utils.toWei(String(amount)), // TODO: Figure out
      gasPrice: rskClient.utils.toHex(5 * Math.pow(10, 9)),
      gas: rskClient.utils.toHex(318730),
      gasLimit: rskClient.utils.toHex(318730)
    };

    ethereum.request(
      {
        method: 'eth_sendTransaction',
        params: [tx_args],
      },
      (error, result) => callback(error, ethereum.selectedAddress, result)
    );

  } else {
    // ERC 20 for RSK
  }


  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to: ' + error) }, 'error');
      console.log(error);
    } else {

      const payload = {
        payout_type: 'rsk_ext',
        tenant: 'RSK',
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
          _alert('Unable to make payout bounty. Please try again later', 'error');
          console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        _alert('Unable to make payout bounty. Please try again later', 'error');
        console.log(error);
      });
    }
  }
};