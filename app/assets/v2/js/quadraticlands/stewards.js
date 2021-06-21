document.addEventListener('DOMContentLoaded', function() {

  // load an error view first - just in case somebody is NOT on right network
  updateInterface('ineligible');

  // every time web3 is ready / address changes this calls the async function delegationInterface()
  document.addEventListener('dataWalletReady', stewardsInterface);

  // all stewards cards
  const stewards = document.querySelectorAll('.steward-card');

  // get all delegate buttons
  const btnStewardSelect = document.querySelectorAll('.button-steward-select');

  // map each button
  btnStewardSelect.forEach(steward => {
    steward.addEventListener('click', () => {

      console.debug('steward address', steward.dataset.address);

      setDelegateAddress(steward.dataset.address, gtc_address());

      // reset current selection (by remove classes from all cards) in interface
      stewards.forEach(steward => {
        steward.classList.remove('selected');
      });

      // select a steward in interface
      delegate = steward.closest('.steward-card');
      delegate.classList.add('selected');

    });
  });

});


async function stewardsInterface() {

  try {

    let balance = await getTokenBalances(gtc_address());
    let delegateAddress = await getDelegateAddress(gtc_address(), selectedAccount);

    console.debug('Balance', balance.balance);
    console.debug('DelegateAddress', delegateAddress);

    if (selectedAccount && balance.balance > 0) {
      updateInterface('stewards');
    } else {
      updateInterface('ineligible');
    }

  } catch (e) {
    console.error('There was an error getting balance and/or delegate address', e);
  }

}


// interface
// (  will be also externally called with "pending", "success", "error" by setDelegateAddress in ql-web3.js )

function updateInterface(status = 'pending', transactionHash = '') {

  console.debug('UPDATEINTERFACE');

  blockExplorerName = 'Etherscan';

  interface_stewards = document.getElementById('interface_stewards');
  interface_ineligible = document.getElementById('interface_ineligible');
  interface_tx_pending = document.getElementById('interface_tx_pending');
  interface_tx_error = document.getElementById('interface_tx_error');

  transaction_link_pending = document.getElementById('transaction_link_pending');
  transaction_link_error = document.getElementById('transaction_link_error');

  if (status == 'stewards') {
    interface_stewards.classList.remove('hide');
    interface_ineligible.classList.add('hide');
    interface_tx_pending.classList.add('hide');
    interface_tx_error.classList.add('hide');
    console.debug('UPDATEINTERFACE:STEWARDS');
  } else if (status == 'ineligible') {
    interface_stewards.classList.add('hide');
    interface_ineligible.classList.remove('hide');
    interface_tx_pending.classList.add('hide');
    interface_tx_error.classList.add('hide');
    console.debug('UPDATEINTERFACE:INELIGIBLE');
  } else if (status == 'pending') {
    tx_link = get_etherscan_url(transactionHash, document.web3network);
    link = "<a target='_blank' href='" + tx_link + "'>" + blockExplorerName + '</a>';
    transaction_link_pending.innerHTML = link;
    transaction_link_error.innerHTML = link;
    flashMessage('Transaction pending', 5000);

    interface_stewards.classList.add('hide');
    interface_ineligible.classList.add('hide');
    interface_tx_pending.classList.remove('hide');
    interface_tx_error.classList.add('hide');
    console.debug('UPDATEINTERFACE:PENDING');
  } else if (status == 'success') {
    flashMessage('Transaction successfull', 5000);
    console.debug('UPDATEINTERFACE:SUCCESS');
    window.location = '/quadraticlands/dashboard';
  } else if (status == 'error') {
    flashMessage('Transaction Error', 3000);

    interface_stewards.classList.add('hide');
    interface_ineligible.classList.add('hide');
    interface_tx_pending.classList.add('hide');
    interface_tx_error.classList.remove('hide');
    console.error('UPDATEINTERFACE:ERROR');
  }
}
