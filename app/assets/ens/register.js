window.onload = function() {
  $('#register')[0].onclick = function(e) {
    if ($('#tos')[0].checked === false) {
      return alert('Please check the TOS checkbox.');
    }
    if (typeof web3 == 'undefined') {
      return alert('Please install metamask in your browser and try again.');
    }
    // Get the github handle
    githubHandle = $('#githubHandle').text();
    // Get the current account and call sign function:
    web3.eth.getAccounts(function(err, accounts) {
      if (!accounts)
        return;
      signMsgAndCreateSubdomain('Github Username : ' + $('#githubHandle').text(), accounts[0]);
    });
  };
};
