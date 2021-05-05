document.addEventListener('DOMContentLoaded', function() {

  // every time web3 is ready / address changes this calls the async function delegationInterface()
  document.addEventListener('dataWalletReady', delegationInterface);

  // defining the interface elements
  const governance = document.getElementById('governance');
  const delegation_mode = document.getElementById('delegation_mode');
  const toggle_disabled = document.getElementById('toggle_disabled');
  const toggle_enabled = document.getElementById('toggle_enabled');
  const delegate_address = document.getElementById('delegate_address');
  const txt_delegate = document.getElementById('txt_delegate');
  const txt_redelegate = document.getElementById('txt_redelegate');
  const txt_disable_delegate = document.getElementById('txt_disable_delegate');
  const delegate_button = document.getElementById('delegate_button');
  const delegate_input = document.getElementById('delegate_input');
  const toggle_button_enabled = document.getElementById('toggle_button_enabled');

  // validate delegate address input field > recolor delegate button
  delegate_input.addEventListener('input', () => {
    delegate_button.classList.add('disabled');
    // check if this address is a valid address
    if (web3.utils.toChecksumAddress(delegate_input.value)) {
      delegate_button.classList.remove('disabled');
    }
  });

  // defining enabled delegate button : web3 delegate(selectedAccount)
  toggle_enabled.addEventListener('click', () => {
    if (selectedAccount) {
      console.debug('DELEGATE TO (SELF) : ' + selectedAccount);
      // call a function like delegate(selectedAccount) ( what is basically selfdelegation )
      setDelegateAddress(selectedAccount, gtc_address());
    }
  });

  // special effect : on enbled button on hover show disabled button
  toggle_enabled.addEventListener('mouseover', () => {
    toggle_button_enabled.classList.add('disabled');
    toggle_button_enabled.classList.remove('enabled');
  });
  toggle_enabled.addEventListener('mouseout', () => {
    toggle_button_enabled.classList.add('enabled');
    toggle_button_enabled.classList.remove('disabled');
  });

  // defining the delegate button : web3 delegate(delegate_input.value)
  delegate_button.addEventListener('click', () => {
    if (selectedAccount) {
      console.debug('DELEGATE TO ' + delegate_input.value);
      setDelegateAddress(delegate_input.value, gtc_address());
    }
  });

});


async function delegationInterface() {

  try {

    let balance = await getTokenBalances(gtc_address());
    let delegateAddress = await getDelegateAddress(gtc_address(), selectedAccount);

    console.debug('Balance', balance.balance);
    console.debug('DelegateAddress', delegateAddress);

    if (selectedAccount && balance.balance > 0) {

      governance.classList.remove('hide');

      if (selectedAccount == delegateAddress) {
        // DISABLED
        delegation_mode.innerHTML = 'disabled';
        toggle_disabled.classList.remove('hide');
        toggle_enabled.classList.add('hide');
        txt_delegate.classList.remove('hide');
        txt_redelegate.classList.add('hide');
        txt_disable_delegate.classList.add('hide');
        console.debug('DELEGATION MODE : DISABLED');
      } else {
        // ENABLED
        delegation_mode.innerHTML = 'enabled';
        toggle_disabled.classList.add('hide');
        toggle_enabled.classList.remove('hide');
        delegate_address.innerHTML = '( ' + truncate(delegateAddress) + ' )';
        txt_delegate.classList.add('hide');
        txt_redelegate.classList.remove('hide');
        txt_disable_delegate.classList.remove('hide');
        delegate_input.value = delegateAddress;
        console.debug('DELEGATION MODE : ENABLED');
      }

    } else {
      // hide governance module
      governance.classList.add('hide');
    }

  } catch (e) {
    console.log(e);
  }
}

// tx interface handling
function updateInterface(status = 'pending', transactionHash = '') {
  blockExplorerName = 'Etherscan';

  tx_pending = document.getElementById('tx_pending');
  tx_error = document.getElementById('tx_error');
  transaction_link_pending = document.getElementById('transaction_link_pending');
  transaction_link_error = document.getElementById('transaction_link_error');

  if (status == 'pending') {

    tx_link = get_etherscan_url(transactionHash, document.web3network);
    link = "<a target='_blank' href='" + tx_link + "'>" + blockExplorerName + '</a>';
    transaction_link_pending.innerHTML = link;
    transaction_link_error.innerHTML = link;

    flashMessage('Transaction pending', 5000);
    governance.classList.add('hide');
    tx_pending.classList.remove('hide');

  } else if (status == 'success') {

    flashMessage('Transaction successful', 5000);
    window.location = '/quadraticlands/dashboard';

  } else if (status == 'error') {

    tx_pending.classList.add('hide');
    tx_error.classList.remove('hide');
    flashMessage('Transaction Error', 3000);

  }
}
