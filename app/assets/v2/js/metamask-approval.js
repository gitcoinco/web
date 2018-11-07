async function metamaskApproval() {
  if (window.ethereum) {
    window.web3 = new Web3(ethereum);
    is_metamask_approved = await window.ethereum._metamask.isApproved();
    is_metamask_unlocked = await window.ethereum._metamask.isUnlocked();

    try {
      if (is_metamask_unlocked && is_metamask_approved) {
        await ethereum.enable();
      }
    } catch (error) {

    }
  }
}

window.addEventListener('load', metamaskApproval);
