window.onload = function() {
  $('#register')[0].onclick = function(e) {
    if ($('#tos')[0].checked === false) {
      return _alert({ message: gettext('Please check the TOS checkbox.')}, 'error');
    }
    if (!window.web3.currentProvider) {
      return _alert({ message: gettext('Please install MetaMask in your browser and try again.')}, 'error');
    }
    // Get the github handle
    githubHandle = $('#githubHandle').text();
    // call the sign function:
    signMsgAndCreateSubdomain('Github Username : ' + $('#githubHandle').text(), document.coinbase);
  };
};
