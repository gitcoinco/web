const payWithRSKExtension = async (fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  // 1. init rsk provider
  const rskHost = "https://public-node.testnet.rsk.co";
  // const rskHost = "https://public-node.rsk.co";
  const rskClient = new Web3();
  rskClient.setProvider(
    new rskClient.providers.HttpProvider(rskHost)
  );

  // TODO: Prompt user to unlock wallet if ethereum.selectedAddress is not present
  // TODO: Add check to see if balance is present

  // 2. construct + sign txn via nifty
  if (token_name == 'R-BTC') {
    const tx_args = {
      to: to_address.toLowerCase(),
      from: ethereum.selectedAddress,
      value: rskClient.utils.toHex(rskClient.utils.toWei(String(amount))),
      gasPrice: rskClient.utils.toHex(await rskClient.eth.getGasPrice()),
      gas: rskClient.utils.toHex(318730),
      gasLimit: rskClient.utils.toHex(318730)
    };

    const txHash = await ethereum.request(
      {
        method: 'eth_sendTransaction',
        params: [tx_args],
      }
    );

    callback(null, ethereum.selectedAddress, txHash)

  } else {
    // TODO: figure out data format
    // ERC 20 for RSK

    // DOC - 18 - 0xe700691da7b9851f2f35f8b8182c69c53ccad9db
    // RDOC - 18 - 0x2d919f19d4892381d58edebeca66d5642cef1a1f

    const amountInWei = rskClient.utils.toHex(rskClient.utils.toWei(String(amount)));
    const encoded_amount = new rskClient.utils.BN(BigInt(amountInWei)).toString();
    const token_contract = new rskClient.eth.Contract(token_abi, vm.bounty.token_address);
    const data = token_contract.methods.transfer(to_address.toLowerCase(), encoded_amount).encodeABI();

    const tx_args = {
      to: to_address.toLowerCase(),
      from: ethereum.selectedAddress,
      value: '0x0',
      gasPrice: rskClient.utils.toHex(await rskClient.eth.getGasPrice()),
      gas: rskClient.utils.toHex(318730),
      gasLimit: rskClient.utils.toHex(318730),
      data: data
    };

    const txHash = await ethereum.request(
      {
        method: 'eth_sendTransaction',
        params: [tx_args],
      }
    );

    callback(null, ethereum.selectedAddress, txHash)
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