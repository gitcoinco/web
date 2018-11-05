async function metamaskApproval() {
  if (window.ethereum) {
    window.web3 = new Web3(ethereum);
    var approved = await window.ethereum._metamask.isApproved();
    
    try {
      if (approved) {
        await ethereum.enable();
      }
    } catch (error) {

    }
  }
}

window.addEventListener('load', metamaskApproval);
