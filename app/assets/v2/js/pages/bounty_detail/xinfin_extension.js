const payWithXinfinExtension = async(fulfillment_id, to_address, vm, modal) => {

  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;

  try {
    web3.version.getNetwork(async(err, providerNetworkId) => {
      // 1. init provider
      await ethereum.enable();
      xdc3Client = await new xdc3(web3.currentProvider);

      // 2. check if default account is selected
      if (web3.eth.defaultAccount == null) {
        modal.closeModal();
        _alert({ message: 'Please unlock XinPay Wallet extension' }, 'danger');
        return;
      }

      // 3. check if token is XDC
      if (token_name == 'XDC') {

        const xdcBalance = await xdc3Client.eth.getBalance(web3.eth.defaultAccount);

        if (Number(xdcBalance) < Number(amount * 10 ** 18)) {
          _alert({ message: `insufficient balance in address ${web3.eth.defaultAccount}` }, 'danger');
          return;
        }

        let txArgs = {
          to: to_address.toLowerCase(),
          from: web3.eth.defaultAccount,
          value: (amount * 10 ** 18).toString()
        };

        xdc3Client.eth.sendTransaction(
          txArgs,
          (error, result) => callback(error, web3.eth.defaultAccount, result)
        );

      } else {
        modal.closeModal();
        _alert({ message: 'XinPay supports payouts in XDC only.' }, 'danger');
        return;
      }
    });

  } catch (e) {
    modal.closeModal();
    _alert({ message: 'Please download or enable XinPay Wallet extension' }, 'danger');
    return;
  }

  function callback(error, from_address, txn) {
    if (error) {
      _alert({ message: gettext('Unable to payout bounty due to: ' + error) }, 'danger');
      console.log(error);
    } else {

      const payload = {
        payout_type: 'xinfin_ext',
        tenant: 'XINFIN',
        amount: amount,
        token_name: token_name,
        funder_address: from_address.replace(/^(0x)/, 'xdc'),
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
      }).catch(function(error) {
        _alert('Unable to make payout bounty. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
