const contributeWithCosmosExtension = async(grant, vm) => {
  let decimals = vm.filterByChainId.filter(token => {
    return token.name == grant.grant_donation_currency;
  })[0].decimals;
  const amount = grant.grant_donation_amount * 10 ** decimals;
  const to_address = grant.cosmos_payout_address;
  const chainId = 'cosmoshub-4';

  if (!window.keplr) {
    _alert({ message: gettext('Please download or enable Keplr browser wallet extension.') }, 'danger');
  }

  try {
    await window.keplr.enable(chainId);
  } catch (e) {
    _alert({ message: gettext('Please unlock Keplr browser wallet extension.') }, 'danger');
    return;
  }

  let client = await window.CosmWasmJS.setupWebKeplr({
    chainId,
    rpcEndpoint: `${window.location.origin}/api/v1/reverse-proxy/cosmos`,
    gasPrice: '0.0008uatom'
  });

  const from_address = (await client.signer.getAccounts())[0].address;

  let atomBalance = (await client.getBalance(from_address, 'uatom')).amount;

  if (Number(atomBalance) < amount) {
    _alert({ message: gettext(`Insufficient balance in address ${from_address}`) }, 'danger');
    return;
  }

  try {
    const result = await client.sendTokens(
      from_address,
      to_address,
      [{ amount: amount.toString(), denom: 'uatom' }],
      'auto'
    );

    if (result.code !== undefined && result.code !== 0) {
      throw new Error(result.log || result.rawLog);
    }

    callback(null, from_address, result.transactionHash);
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
          'tenant': 'COSMOS',
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {
        if (200 <= response.status && response.status <= 204) {
          EmailPreferenceEvent.createEvent({
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
