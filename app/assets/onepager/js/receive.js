/* eslint-disable no-console */
window.onload = function() {
  waitforWeb3(function() {
    if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
    } else {
      $('#forwarding_address').val(web3.eth.coinbase);
    }
    $('#network').val(document.web3network);
  });
};