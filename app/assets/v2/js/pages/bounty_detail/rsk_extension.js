const payWithRSKExtension = async (fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  // 1. init rsk provider
  // const rskHost = "https://public-node.testnet.rsk.co";
  const rskHost = "https://public-node.rsk.co";
  const rskClient = new Web3();
  rskClient.setProvider(
    new rskClient.providers.HttpProvider(rskHost)
  );

  // 2. check if wallet ins installed and unlocked
  if (!provider) {
    try {
      console.log(ethereum.selectedAddress);
    } catch (e) {
      modal.closeModal();
      _alert({ message: 'Please download or enable Nifty Wallet extension' }, 'danger');
      return;
    }

    if (!ethereum.selectedAddress) {
      modal.closeModal();
      return onConnect().then(() => {
        modal.openModal();
      });
    }
  }

  // 2. construct + sign txn via nifty
  let txArgs;

  if (token_name == 'RBTC') {

    balanceInWei = await rskClient.eth.getBalance(ethereum.selectedAddress);

    rbtcBalance = rskClient.utils.fromWei(balanceInWei, 'ether');

    if (Number(rbtcBalance) < amount) {
      _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'danger');
      return;
    }

    txArgs = {
      to: to_address.toLowerCase(),
      from: ethereum.selectedAddress,
      value: rskClient.utils.toHex(rskClient.utils.toWei(String(amount))),
      gasPrice: rskClient.utils.toHex(await rskClient.eth.getGasPrice()),
      gas: rskClient.utils.toHex(318730),
      gasLimit: rskClient.utils.toHex(318730)
    };

  } else {

    tokenContract = new rskClient.eth.Contract(token_abi, vm.bounty.token_address);

    balance = tokenContract.methods.balanceOf(
      ethereum.selectedAddress).call({ from: ethereum.selectedAddress });

    amountInWei = amount * 1.0 * Math.pow(10, vm.decimals);

    if (Number(balance) < amountInWei) {
      _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'danger');
      return;
    }

    amountAsString = new rskClient.utils.BN(BigInt(amountInWei)).toString();
    data = tokenContract.methods.transfer(to_address.toLowerCase(), amountAsString).encodeABI();

    txArgs = {
      to: vm.bounty.token_address,
      from: ethereum.selectedAddress,
      gasPrice: rskClient.utils.toHex(await rskClient.eth.getGasPrice()),
      gas: rskClient.utils.toHex(318730),
      gasLimit: rskClient.utils.toHex(318730),
      data: data
    };
  }

  const txHash = await ethereum.request(
    {
      method: 'eth_sendTransaction',
      params: [txArgs],
    }
  );

  callback(null, ethereum.selectedAddress, txHash)

  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to: ' + error) }, 'danger');
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
          _alert('Payment Successful', 'success');

        } else {
          _alert('Unable to make payout bounty. Please try again later', 'danger');
          console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function (error) {
        _alert('Unable to make payout bounty. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
