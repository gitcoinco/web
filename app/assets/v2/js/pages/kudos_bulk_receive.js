$(document).ready(function() {
  if (!$('#user').val()) {
    $('#receive').attr('disabled', 'disabled');
  }

  waitforWeb3(function() {
    if (document.web3network == 'locked') {
      _alert('Metamask not connected. <button id="metamask_connect" onclick="approve_metamask()">Click here to connect to metamask</button>', 'error');
    } else if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
      $('#receive').attr('disabled', 'disabled');
    } else {
      $('#forwarding_address').val(web3.eth.coinbase);
    }
  });

});