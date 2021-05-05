// force web3Modal to pop up when no Account - even when user logout / looses connection
// this is here to prevent design "no wallet log in bla bla on all that pages that needs a wallet"
document.addEventListener('DOMContentLoaded', function() {
  setInterval(function() {
    if (!selectedAccount) {
      if (!web3Modal.show) {
        onConnect();
      }
    }
  }, 1000);
});
