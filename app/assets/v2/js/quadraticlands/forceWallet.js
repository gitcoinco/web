// force web3Modal to pop up when no Account - even when user logout / looses connection
// this is here to prevent design "no wallet log in bla bla on all that pages that needs a wallet"
document.addEventListener('DOMContentLoaded', async function() {
  if (!web3Modal) {
    needWalletConnection();
  } else if (!provider) {
    await onConnect();
  }
});
