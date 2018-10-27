disabled = ['/', '/how/funder', '/how/contributor', '/tools'];

async function metamaskApproval() {
  if (window.ethereum) {
    window.web3 = new Web3(ethereum);
    try {
      if ($.inArray(window.location.pathname, disabled) == -1) {
        await ethereum.enable();
      }
    } catch (error) {
      console.log('user denied access');
    }
  }
}

window.addEventListener('load', metamaskApproval);
