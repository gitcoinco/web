var legacy_bounty_abi = [{'inputs': [{'type': 'uint256', 'name': ''}], 'constant': true, 'name': 'bounty_indices', 'outputs': [{'type': 'bytes32', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'bytes32', 'name': ''}], 'constant': true, 'name': 'bountiesbyrepo', 'outputs': [{'type': 'uint256', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': 'str'}], 'constant': false, 'name': 'normalizeIssueURL', 'outputs': [{'type': 'string', 'name': 'result'}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': 'str'}], 'constant': false, 'name': 'getRepoURL', 'outputs': [{'type': 'string', 'name': 'result'}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_issueURL'}, {'type': 'uint256', 'name': '_amount'}, {'type': 'address', 'name': '_tokenAddress'}, {'type': 'uint256', 'name': '_expirationTimeDelta'}, {'type': 'string', 'name': '_metaData'}], 'constant': false, 'name': 'postBounty', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': true, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'numBounties', 'outputs': [{'type': 'uint256', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_repoURL'}], 'constant': false, 'name': 'getNumberBounties', 'outputs': [{'type': 'uint256', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_issueURL'}, {'type': 'string', 'name': '_claimee_metaData'}], 'constant': false, 'name': 'claimBounty', 'outputs': [], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_issueURL'}], 'constant': false, 'name': 'clawbackExpiredBounty', 'outputs': [], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_issueURL'}], 'constant': false, 'name': 'rejectBountyClaim', 'outputs': [], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_issueURL'}], 'constant': false, 'name': 'bountydetails', 'outputs': [{'type': 'uint256', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'bool', 'name': ''}, {'type': 'bool', 'name': ''}, {'type': 'string', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'string', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'string', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'bytes32', 'name': 'index'}], 'constant': false, 'name': '_bountydetails', 'outputs': [{'type': 'uint256', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'address', 'name': ''}, {'type': 'bool', 'name': ''}, {'type': 'bool', 'name': ''}, {'type': 'string', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'string', 'name': ''}, {'type': 'uint256', 'name': ''}, {'type': 'string', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'bytes32', 'name': ''}], 'constant': true, 'name': 'Bounties', 'outputs': [{'type': 'uint256', 'name': 'amount'}, {'type': 'address', 'name': 'bountyOwner'}, {'type': 'address', 'name': 'claimee'}, {'type': 'string', 'name': 'claimee_metaData'}, {'type': 'uint256', 'name': 'creationTime'}, {'type': 'uint256', 'name': 'expirationTime'}, {'type': 'bool', 'name': 'initialized'}, {'type': 'string', 'name': 'issueURL'}, {'type': 'string', 'name': 'metaData'}, {'type': 'bool', 'name': 'open'}, {'type': 'address', 'name': 'tokenAddress'}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': '_issueURL'}], 'constant': false, 'name': 'approveBountyClaim', 'outputs': [], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'string', 'name': 'str'}], 'constant': false, 'name': 'strToMappingIndex', 'outputs': [{'type': 'bytes32', 'name': 'result'}], 'payable': false, 'type': 'function'}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'string', 'name': 'issueURL'}, {'indexed': false, 'type': 'uint256', 'name': 'amount'}], 'type': 'event', 'name': 'bountyPosted', 'anonymous': false}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'string', 'name': 'issueURL'}], 'type': 'event', 'name': 'bountyClaimed', 'anonymous': false}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'string', 'name': 'issueURL'}], 'type': 'event', 'name': 'bountyExpired', 'anonymous': false}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'address', 'name': 'payee'}, {'indexed': false, 'type': 'string', 'name': 'issueURL'}], 'type': 'event', 'name': 'bountyClaimApproved', 'anonymous': false}, {'inputs': [{'indexed': false, 'type': 'address', 'name': '_from'}, {'indexed': false, 'type': 'string', 'name': 'issueURL'}], 'type': 'event', 'name': 'bountyClaimRejected', 'anonymous': false}];


var legacy_bounty_address = function() {
  switch (document.web3network) {
    case 'mainnet':
      return '0xb10700b5ece20a3c65b047f76fd3dc13720bd30e';
    case 'ropsten':
      return '0x3102118ba636942c82d1a6efa2e7d069dc2d14bd';
    case 'kovan':
      throw 'this network is not supported in bounty_address() for gitcoin';
    case 'rinkeby':
      return '0x361a451ea7ac6b21f4a5f24390405ad113de3f5b';
    case 'custom network':
      return '0x0ed0c2a859e9e576cdff840c51d29b6f8a405bdd';
  }
};

window.onload = function() {
  // a little time for web3 injection
  setTimeout(function() {
    var account = web3.eth.accounts[0];

    if (typeof localStorage['acceptTOS'] != 'undefined' && localStorage['acceptTOS']) {
      $('input[name=terms]').attr('checked', 'checked');
    }
    if (getParam('source')) {
      $('input[name=issueURL]').val(getParam('source'));
    }

    $('#submitBounty').click(function(e) {
      mixpanel.track('Kill Bounty Clicked', {});
      loading_button($('#submitBounty'));
      e.preventDefault();
      var issueURL = $('input[name=issueURL]').val();

      var isError = false;

      if ($('#terms:checked').length == 0) {
        _alert({ message: 'Please accept the terms of service.' });
        isError = true;
      } else {
        localStorage['acceptTOS'] = true;
      }
      if (issueURL == '') {
        _alert({ message: 'Please enter a issue URL.' });
        isError = true;
      }
      if (isError) {
        unloading_button($('#submitBounty'));
        return;
      }

      var bounty = web3.eth.contract(legacy_bounty_abi).at(legacy_bounty_address());

      var bountydetails_callback = function(error, result) {
        console.log('bountydetails_callback');
        if (error) {
          console.error(error);
          _alert('Got an error.  Please screencap your console and reach out to @owocki on slack.');
          unloading_button($('#submitBounty'));
          return;
        }
        var is_open = result[4];

        if (!is_open) {
          _alert('this issue is no longer active (already been paid or already been killed)');
          unloading_button($('#submitBounty'));
          return;
        }
        var claimee_address = result[3];
        var is_claimed = claimee_address != '0x0000000000000000000000000000000000000000' && claimee_address != '0x0';
        var expiration_time = result[9].toNumber();
        var is_expired = timestamp() > expiration_time;

        if (is_expired) {
          // expired: kill bounty
          console.log('1. expired: kill bounty');
          _alert('Please confirm this 1 transaction to clawback the bounty.', 'info');
          bounty.clawbackExpiredBounty.sendTransaction(issueURL, function(error, result) {
            if (error) {
              console.error(error);
              _alert('Got an error.  Please screencap your console and reach out to @owocki on slack.');
              unloading_button($('#submitBounty'));
              return;
            }
            var etherscan_url = etherscan_tx_url(result);

            _alert('Your funds will be returned to you when <a href=' + etherscan_url + '>this transaction</a> is confirmed.', 'info');
          });
        } else {
          // not expired: submit and accept bounty
          console.log('1. not expired: submit and accept bounty');
          var accept_bounty = function() {
            console.log('accept_bounty');
            _alert('Please confirm this 1 transaction to finish killing the bounty.', 'info');
            bounty.approveBountyClaim.sendTransaction(issueURL, {}, function(error, result) {
              if (error) {
                console.error(error);
                _alert('Got an error.  Please screencap your console and reach out to @owocki on slack.');
                unloading_button($('#submitBounty'));
                return;
              }
              var etherscan_url = etherscan_tx_url(result);

              _alert('Your funds will be returned to you when <a href=' + etherscan_url + '>this transaction</a> is confirmed.', 'info');
            });
          };
          var submit_bounty = function() {
            console.log('submit_bounty');
            _alert('Please confirm these 2 transactions to kill the bounty.', 'info');
            bounty.claimBounty.sendTransaction(issueURL, {}, function(error, result) {
              if (error) {
                console.error(error);
                _alert('Got an error.  Please screencap your console and reach out to @owocki on slack.');
                unloading_button($('#submitBounty'));
                return;
                _alert('Please wait for tx to confirm.', 'info');
                callFunctionWhenTransactionMined(result, function() {
                  accept_bounty();
                });
              }
            });
          };

        }
      };

      bounty.bountydetails.call(issueURL, bountydetails_callback);



    });
  }, 100);

};
