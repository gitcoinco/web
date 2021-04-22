const contributeWithRskExtension = async (grant, vm, modal) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const to_address = grant.rsk_payout_address;
  const token = vm.getTokenByName(token_name);

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


  // 3. construct + sign txn via nifty
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

    tokenContract = new rskClient.eth.Contract(token_abi, token.addr);

    balance = tokenContract.methods.balanceOf(
      ethereum.selectedAddress).call({ from: ethereum.selectedAddress });

    amountInWei = amount * 1.0 * Math.pow(10, token.decimals);

    if (Number(balance) < amountInWei) {
      _alert({ message: `Insufficent balance in address ${ethereum.selectedAddress}` }, 'danger');
      return;
    }

    amountAsString = new rskClient.utils.BN(BigInt(amountInWei)).toString();
    data = tokenContract.methods.transfer(to_address.toLowerCase(), amountAsString).encodeABI();

    txArgs = {
      to: token.addr,
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

  callback(null, ethereum.selectedAddress, txHash);

  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'danger');
      console.log(error);
    } else {

      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'RSK',
          'comment': grant.grant_comments,
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = `v1/api/contribute`;

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
          MauticEvent.createEvent({
            'alias': 'products',
            'data': [
              {
                'name': 'product',
                'attributes': {
                  'product': 'grants',
                  'persona': 'grants-contributor',
                  'action': 'contribute'
                }
              }
            ]
          });
          vm.updatePaymentStatus(grant.grant_id, 'done', txn);
        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to make contribute to grant. Please try again later', 'danger');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function (error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to make contribute to grant. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
