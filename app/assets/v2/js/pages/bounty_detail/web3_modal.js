const payWithWeb3 = (fulfillment_id, fulfiller_address,  vm, modal) => {
  
  const amount = vm.fulfillment_context.amount;
  const token_name = vm.bounty.token_name;
  
  web3.eth.sendTransaction({
    to: fulfiller_address,
    from: selectedAccount,
    value: web3.utils.toWei(String(amount)),
    gasPrice: web3.utils.toHex(5 * Math.pow(10, 9)),
    gas: web3.utils.toHex(318730),
    gasLimit: web3.utils.toHex(318730)
  },
  function(error, result) {
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
          _alert('Payment Successful');

        } else {
          _alert('Unable to make payout bounty. Please try again later', 'error');
          console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        _alert('Unable to make payout bounty. Please try again later', 'error');
        console.log(error);
      });
    }
  });
}