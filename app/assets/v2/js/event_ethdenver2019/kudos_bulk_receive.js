$(document).ready(function() {

  setInterval(function() {
    var current_forwarding_address = $('#forwarding_address').val();

    if (current_forwarding_address) {
      console.log('got forwarding address');
      localStorage.setItem('forwarding_address', current_forwarding_address);
    } else if (localStorage['forwarding_address'] && !$('#forwarding_address').is(':focus')) {
      console.log('setting forwarding address');
      $('#forwarding_address').val(localStorage['forwarding_address']);
    }
  }, 100);

  waitforWeb3(function() {
    if (document.web3network == 'locked') {
      _alert('Wallet not connected. <button id="metamask_connect" onclick="onConnect()">Click here to connect a Wallet</button>', 'danger');
    } else if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'danger');
      $('#receive').attr('disabled', 'disabled');
    } else {
      web3.eth.getCoinbase(function(_, coinbase) {
        $('#forwarding_address').val(coinbase);
      });
    }
  });

});
