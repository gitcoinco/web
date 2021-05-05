document.addEventListener('DOMContentLoaded', function() {

  updateInterface('nowallet');

  const receiveAddress = document.getElementById('receiveAddress');

  window.addEventListener('dataWalletReady', () => {
    receiveAddress.innerHTML = selectedAccount;
    updateInterface('ready');
  });

  // check each 2 seconds if user is still connected fetch
  // the edgecase of user logout / gets disconnected
  setInterval(() => {
    if (!selectedAccount) {
      updateInterface('nowallet');
    }
  }, 2000);

  // map buttonConnect button to popup web3modal
  const buttonConnect = document.getElementById('buttonConnect');

  buttonConnect.addEventListener('click', () => {
    onConnect();
  });

});

function updateInterface(status) {

  interface_nowallet = document.getElementById('interface_nowallet');
  interface_ready = document.getElementById('interface_ready');

  if (status == 'nowallet') {
    interface_nowallet.classList.remove('hide');
    interface_ready.classList.add('hide');
    console.debug('INTERFACE:NOWALLET');
  }

  if (status == 'ready') {
    interface_nowallet.classList.add('hide');
    interface_ready.classList.remove('hide');
    console.debug('INTERFACE:READY');
  }

}
