const payWithRSKExtension = async (fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  // init rsk provider
  const rskHost = "https://public-node.testnet.rsk.co";
  // const rskHost = "https://public-node.rsk.co";
  const rskClient = new Web3();
  rskClient.setProvider(
    new rskClient.providers.HttpProvider(rskHost)
  );

  // TODO: Prompt user to unlock wallet if ethereum.selectedAddress is not present

  if (token_name == 'R-BTC') {

    rbtcBalance = rskClient.utils.fromWei(
      rskClient.eth.getBalance(ethereum.selectedAddress),
      'ether'
    );
  
    if (Number(rbtcBalance) < amount) {
      _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'error');
    }

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

    let tokenContractAddress;

    if (token_name === 'DOC') {
      tokenContractAddress = '0xe700691da7b9851f2f35f8b8182c69c53ccad9db';
    } else if (token_name === 'RDOC') {
      tokenContractAddress = '0x2d919f19d4892381d58edebeca66d5642cef1a1f';
    } else if (token_name === 'tRIF') {
      tokenContractAddress = '0x19f64674d8a5b4e652319f5e239efd3bc969a1fe';
    }
    
    tokenContract = new rskClient.eth.Contract(token_abi, token_address);

    balance = tokenContract.methods.balanceOf(
      ethereum.selectedAddress).call({from: ethereum.selectedAddress});

    amountInWei  = amount * 1.0 * Math.pow(10, vm.decimals);

    if (Number(balance) < amountInWei) {
      _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'error');
    }

    amountAsString = new rskClient.utils.BN(BigInt(amountInWei)).toString();
    data = tokenContract.methods.transfer(to_address.toLowerCase(), amountAsString).encodeABI();

    txArgs = {
      to: to_address.toLowerCase(),
      from: ethereum.selectedAddress,
      gasPrice: rskClient.utils.toHex(await rskClient.eth.getGasPrice()),
      data: data
    };

    const txHash = await ethereum.request({ method: 'eth_sendTransaction', params: [txArgs] });

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