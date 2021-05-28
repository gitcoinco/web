document.addEventListener('DOMContentLoaded', function() {
  const web3network = document.querySelector('#web3network');

  // check for network
  document.addEventListener('dataWalletReady', getWeb3Network);

  // hide nowallet icon on existing provider
  document.addEventListener('dataWalletReady', hideNoprovider);

  // check each 2 seconds if user is still connected fetch
  // the edgecase of user logout / gets disconnected

  setInterval(() => {
    if (typeof selectedAccount == 'undefined' || !selectedAccount) {
      showNoprovider();
    }
  }, 2000);
});

// hide noproviderIcon on existing provider
function hideNoprovider() {
  noproviderIcon = document.querySelector('#noproviderIcon');
  if (noproviderIcon) {
    noproviderIcon.classList.add('hide');
  }
}

// hide noproviderIcon on existing provider
function showNoprovider() {
  noproviderIcon = document.querySelector('#noproviderIcon');
  if (noproviderIcon) {
    noproviderIcon.classList.remove('hide');
  }
}

async function getWeb3Network() {
  try {
    let network = await web3.eth.net.getNetworkType();

    if (network == 'main') {
      web3network.classList.add('hide');
      web3network.innerHTML = '';
    } else {
      web3network.innerHTML = network;
      web3network.classList.remove('hide');
    }

  } catch (e) {
    console.log(e);
  }
}
