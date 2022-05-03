const contributeWithHarmonyExtension = async(grant, vm) => {

  // Connect to Harmony Mainnet Shard 0 network with MetaMask
  if (!provider) {
    await onConnect();
  }

  const web3 = new Web3(provider);
  const providerName = window.Web3Modal.getInjectedProviderName();
  const chainInfo = getDataChains(1666600000, 'chainId')[0];
  const chainId = Web3.utils.numberToHex(chainInfo.chainId);

  const amount = grant.grant_donation_amount;
  const to_address = grant.harmony_payout_address;
  const from_address = selectedAccount;

  try {
    await web3.currentProvider.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId }]
    });
  } catch (switchError) {
    // This error code indicates that the chain has not been added to MetaMask
    if (switchError.code === 4902) {

      try {
        await web3.currentProvider.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId,
            rpcUrls: [chainInfo.rpc],
            chainName: chainInfo.name,
            nativeCurrency: chainInfo.nativeCurrency,
            blockExplorerUrls: chainInfo.explorers && chainInfo.explorers.map(e => e.url)
          }]
        });
      } catch (addError) {
        if (addError.code === 4001) {
          throw new Error(`Please connect ${providerName} to ${chainInfo.name} network.`);
        } else {
          console.error(addError);
        }
      }
    } else if (switchError.code === 4001) {
      throw new Error(`Please connect ${providerName} to ${chainInfo.name} network.`);
    } else if (switchError.code === -32002) {
      throw new Error(`Please respond to a pending ${providerName} request.`);
    } else {
      console.error(switchError);
    }
  }

  // Check balance
  const account_balance = web3.utils.fromWei(balance, 'ether');

  if (Number(account_balance) < amount) {
    _alert({ message: `Account needs to have more than ${amount} ONE in shard 0 for payout`}, 'danger');
    return;
  }

  // Payout
  // Gas limit as indicated here: https://docs.harmony.one/home/general/wallets/browser-extensions-wallets/metamask-wallet/sending-and-receiving#sending-a-regular-transaction

  try {
    const txHash = await web3.eth.sendTransaction({
      to: to_address,
      from: from_address,
      value: web3.utils.toWei(String(amount)),
      gasPrice: web3.utils.toHex(30 * Math.pow(10, 9)),
      gas: web3.utils.toHex(25000),
      gasLimit: web3.utils.toHex(25000)
    });

    callback(null, from_address, txHash);
  } catch (e) {
    callback(e);
  }

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
          'tenant': 'HARMONY',
          'amount_per_period': amount
        }]
      };

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
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
          _alert('Unable to contribute to grant. Please try again later', 'danger');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to contribute to grant. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
