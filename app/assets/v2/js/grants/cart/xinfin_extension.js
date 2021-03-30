const contributeWithXinfinExtension = async (grant, vm, modal) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const to_address = grant.rsk_payout_address;
  const token = vm.getTokenByName(token_name);

  // 1. init xinfin provider
  const provider = await detectEthereumProvider();
  await ethereum.enable();
  let xdc3Client = new xdc3(provider);
  const [from_address] = await await xdc3Client.eth.getAccounts()


  // 2. check if wallet ins installed and unlocked
  if (!provider) {

    if (from_address == null) {
      modal.closeModal();
      _alert({ message: 'Please download or enable Xinfin extension' }, 'error');
      return;
    }
  }


  // 3. construct + sign txn via xinpay
  const xdcBalance = await xdc3Client.eth.getBalance(from_address);

  if (Number(xdcBalance) < Number(amount * 10 ** 18)) {
    _alert({ message: `Insufficent balance in address ${from_address}` }, 'error');
    return;
  }
  
  const txArgs = {
    to: to_address.toLowerCase(),
    from: from_address,
    value: (amount * 10 ** 18).toString(),
  };

  xdc3Client.eth.sendTransaction(
    txArgs,
    (error, result) => callback(error, from_address, result)
  );


  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'error');
      console.log(error);
    } else {

      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'XINFIN',
          'comment': grant.grant_comments,
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = `v1/api/contribute`;

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
          vm.updatePaymentStatus(grant.grant_id, 'done', txn);
        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to make contribute to grant. Please try again later', 'error');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function (error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to make contribute to grant. Please try again later', 'error');
        console.log(error);
      });
    }
  }
};
