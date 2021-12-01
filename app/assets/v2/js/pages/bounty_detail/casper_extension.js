const payWithCasperExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;
  const tenant = vm.getTenant(token_name, vm.bounty.web3_type);

  const { CasperClient, DeployUtil, CLPublicKey, Signer } = window;
  const casperClient = new CasperClient(`/api/v1/reverse-proxy/${tenant}`);

  const isConnected = await Signer.isConnected();

  if (!isConnected) {
    try {
      Signer.sendConnectionRequest();
    } catch (e) {
      _alert({ message: gettext('Please download or enable CasperLabs Signer extension.') }, 'danger');
      return;
    }
  }

  let selectedAddress;

  try {
    selectedAddress = await Signer.getActivePublicKey();
  } catch (e) {
    modal.closeModal();
    _alert({ message: gettext('Please unlock CasperLabs Signer extension.') }, 'danger');
    return;
  }

  const paymentAmount = 10000; // for native-transfers the payment price is fixed
  const id = fulfillment_id;
  const gasPrice = 1; // gasPrice for native transfers can be set to 1

  // time that the deploy will remain valid for, in milliseconds
  // the default value is 1800000 ms (30 minutes)
  const ttl = 1800000;

  const fromPublicKey = CLPublicKey.fromHex(selectedAddress);
  const toPublicKey = CLPublicKey.fromHex(to_address);
  
  let deployParams = new DeployUtil.DeployParams(fromPublicKey, 'casper', gasPrice, ttl);

  const session = DeployUtil.ExecutableDeployItem.newTransfer(
    amount * 10 ** vm.decimals,
    toPublicKey,
    null,
    id
  );
  
  const payment = DeployUtil.standardPayment(paymentAmount);
  const deploy = DeployUtil.makeDeploy(deployParams, session, payment);
  const deployJson = DeployUtil.deployToJson(deploy);

  const signedDeployJson = await Signer.sign(deployJson, selectedAddress, to_address);
  const signedDeploy = DeployUtil.deployFromJson(signedDeployJson);

  try {
    const deployHash = await casperClient.putDeploy(signedDeploy);

    callback(null, selectedAddress, deployHash);
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
        payout_type: 'casper_ext',
        tenant: 'CASPER',
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
          