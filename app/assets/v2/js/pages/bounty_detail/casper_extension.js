const payWithCasperExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  const { CasperClient, DeployUtil, PublicKey, Signer } = casper;
  const casperClient = new CasperClient('http://3.142.224.108:7777/rpc');

  const isConnected = await Signer.isConnected();

  if (!isConnected) {
    try {
      Signer.sendConnectionRequest();
    } catch (e) {
      _alert({ message: gettext('Please download or enable CasperLabs Signer extension.') }, 'danger');
    }
  }

  const selectedAddress = await Signer.getActivePublicKey();

  const paymentAmount = 10000;
  const id = fulfillment_id;
  const ttl = 1800000;
  const fromPublicKey = PublicKey.fromHex(selectedAddress);
  const toPublicKey = PublicKey.fromHex(to_address);
  
  let deployParams = new DeployUtil.DeployParams(fromPublicKey, 'casper', ttl);

  const session = DeployUtil.ExecutableDeployItem.newTransfer(
    amount * 10 ** vm.decimals,
    toPublicKey,
    fromPublicKey,
    id
  );
  
  const payment = DeployUtil.standardPayment(paymentAmount);
  const deploy = DeployUtil.makeDeploy(deployParams, session, payment);

  const signedDeploy = await Signer.sign(deploy, fromPublicKey, toPublicKey);

  try {
    const deployHash = await casperClient.putDeploy(signedDeploy);

    callback(null, selectedAddress, deployHash);
  } catch (e) {
    modal.closeModal();
    callback(err);
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
          