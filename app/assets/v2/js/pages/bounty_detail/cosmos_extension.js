const payWithCosmosExtension = async(fulfillment_id, to_address, vm, modal) => {
  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;
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

  const offlineSigner = window.getOfflineSigner(chainId);
  const selectedAddress = (await offlineSigner.getAccounts())[0].address;
    
  // Initialize the gaia api with the offline signer that is injected by Keplr extension.
  // TODO: we need a js browser script from which to access SigningStargateClient
  // stuff like say -> import { SigningStargateClient } from '@cosmjs/stargate';
  const cosmJS = new SigningStargateClient(
    'https://lcd-cosmoshub.keplr.app/rest',
    selectedAddress,
    offlineSigner
  );

  try {
    const result = await cosmJS.sendTokens(recipient, [{
      denom: 'uatom',
      amount: amount.toString()
    }]);

    if (result.code !== undefined && result.code !== 0) {
      throw new Error(result.log || result.rawLog);
    }
  
    callback(null, selectedAddress, result.transactionHash);
  } catch (e) {
    modal.closeModal();
    callback(e);
  }
      
  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to: ' + error) }, 'danger');
      console.log(error);
    } else {
          
      const payload = {
        payout_type: 'cosmos_ext',
        tenant: 'COSMOS',
        amount: amount,
        token_name: token_name,
        funder_address: from_address,
        payout_tx_id: txn
      };
          
      modal.closeModal();
      const apiUrlBounty = `/api/v1/bounty/payout/${fulfillment_id}`;
          
      fetchData(apiUrlBounty, 'POST', payload).then(response => {
        if (200 <= response.status && response.status <= 204) {
          vm.fetchBounty();
          _alert('Payment Successful', 'success');
              
        } else {
          _alert('Unable to make payout bounty. Please try again later', 'danger');
          console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        _alert('Unable to make payout bounty. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
            