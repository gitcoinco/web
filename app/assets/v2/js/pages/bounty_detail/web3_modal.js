const payWithWeb3 = (fulfillment_id, fulfiller_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  if (!provider) {
    modal.closeModal();
    return onConnect().then(() => {
      modal.openModal();
    });
  }

  if (token_name == 'ETH') {
    web3.eth.sendTransaction(
      {
        to: fulfiller_address,
        from: selectedAccount,
        value: web3.utils.toWei(String(amount)),
        gasPrice: web3.utils.toHex(5 * Math.pow(10, 9)),
        gas: web3.utils.toHex(318730),
        gasLimit: web3.utils.toHex(318730)
      },
      (error, result) => callback(error, result)
    );
  } else if (token_name == 'ONE') {
    // Gas limit as indicated here: https://docs.harmony.one/home/general/wallets/browser-extensions-wallets/metamask-wallet/sending-and-receiving#sending-a-regular-transaction
    web3.eth.sendTransaction(
      {
        to: fulfiller_address,
        from: selectedAccount,
        value: web3.utils.toWei(String(amount)),
        gasPrice: web3.utils.toHex(30 * Math.pow(10, 9)),
        gas: web3.utils.toHex(25000),
        gasLimit: web3.utils.toHex(25000)
      },
      (error, result) => callback(error, result)
    );
  } else {

    const amountInWei = amount * 1.0 * Math.pow(10, vm.decimals);
    const amountAsString = new web3.utils.BN(BigInt(amountInWei)).toString();
    const token_contract = new web3.eth.Contract(token_abi, vm.bounty.token_address);

    token_contract.methods.transfer(fulfiller_address, web3.utils.toHex(amountAsString)).send(
      {
        from: selectedAccount
      },
      (error, result) => callback(error, result)
    );
  }

  function callback(error, result) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty. Please try again.') }, 'error');
      console.log(error);
    } else {

      const payload = {
        payout_type: 'web3_modal',
        tenant: 'ETH',
        amount: amount,
        token_name: token_name,
        funder_address: selectedAccount,
        payout_tx_id: result,
        payout_status: 'done'
      };

      modal.closeModal();
      const apiUrlBounty = `/api/v1/bounty/payout/${fulfillment_id}`;

      fetchData(apiUrlBounty, 'POST', payload).then(response => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);

          vm.fetchBounty();
          _alert('Payment Successful', 'success');

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
