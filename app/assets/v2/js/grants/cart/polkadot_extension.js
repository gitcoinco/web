const initPolkadotConnection = async(grant, vm) => {

  // step 1: check if web3 is injected
  if (!polkadot_utils.isWeb3Injected()) {
    vm.updatePaymentStatus(grant.grant_id, 'failed');
    _alert({ message: 'Please ensure your Polkadot One wallet is installed and unlocked'}, 'danger');
    return;
  }

  // step 2: init connection based on token
  let polkadot_endpoint;
  let decimals;
  let format;

  if (grant.grant_donation_currency == 'KSM') {
    polkadot_endpoint = KUSAMA_ENDPOINT;
    decimals = 12;
    format = 0;
  } else if (grant.grant_donation_currency == 'DOT') {
    polkadot_endpoint = POLKADOT_ENDPOINT;
    decimals = 10;
    format = 2;
  }

  polkadot_utils.connect(polkadot_endpoint).then(() =>{
    polkadot_extension_dapp.web3Enable('gitcoin').then(() => {
      initComplete(null, grant, vm);
    }).catch(err => {
      initComplete(err);
    });
  }).catch(err => {
    console.log(err);
    _alert('Error connecting to Polkadot network', 'danger');
  });

  // step 3: allow user to select address on successful connection
  async function initComplete(error, grant, vm) {

    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert('Please ensure you\'ve connected your Polkadot extension to Gitcoin', 'danger');
      console.log(error);
      return;
    }

    const addresses = await polkadot_utils.getExtensionConnectedAccounts();

    for (let i = 0; i < addresses.length; i++) {
      const balance = (await polkadot_utils.getAddressBalance(addresses[i].address)) / 10 ** decimals;

      addresses[i].balance = balance;
      addresses[i].token_symbol = grant.grant_donation_currency;
      addresses[i].chain_address = polkadot_keyring.encodeAddress(addresses[i].address, format);
      addresses[i].sufficent_balance = balance >= grant.grant_donation_amount;
    }

    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {addresses: addresses});
  }
};


const contributeWithPolkadotExtension = async(grant, vm, from_address) => {

  let decimals;

  if (grant.grant_donation_currency == 'KSM') {
    decimals = 12;
  } else if (grant.grant_donation_currency == 'DOT') {
    decimals = 10;
  }

  // step 1. set modal to waiting state
  vm.updatePaymentStatus(grant.grant_id, 'waiting');

  const amount = grant.grant_donation_amount;

  let to_address;

  if (grant.grant_donation_currency == 'DOT') {
    to_address = grant.polkadot_payout_address;
  } else if (grant.grant_donation_currency == 'KSM') {
    to_address = grant.kusama_payout_address;
  }

  // step 2. balance check
  const account_balance = await polkadot_utils.getAddressBalance(from_address);

  if (account_balance < amount * 10 ** decimals) {
    _alert({ message: `Account needs to have more than ${amount} ${grant.grant_donation_currency}`}, 'danger');
    return;
  }

  // step 3: payout
  polkadot_utils.transferViaExtension(
    amount * 10 ** decimals,
    to_address,
    from_address
  ).then(txn => {
    callback(null, from_address, txn.hash.toString());
  }).catch(err => {
    callback(err);
  });


  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'danger');
      console.log(error);
    } else {

      let tenant;

      if (grant.grant_donation_currency == 'DOT') {
        tenant = 'POLKADOT';
      } else if (grant.grant_donation_currency == 'KSM') {
        tenant = 'KUSAMA';
      }

      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': tenant,
          'amount_per_period': grant.grant_donation_amount
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
