/* eslint-disable no-console */
window.onload = function() {
  // a little time for web3 injection
  setTimeout(function() {
    var account = web3.eth.accounts[0];

    if (typeof localStorage['githubUsername'] != 'undefined') {
      if (!$('input[name=githubUsername]').val()) {
        $('input[name=githubUsername]').val(localStorage['githubUsername']);
      }
    }
    if (typeof localStorage['notificationEmail'] != 'undefined') {
      $('input[name=notificationEmail]').val(localStorage['notificationEmail']);
    }
    if (typeof localStorage['acceptTOS'] != 'undefined' && localStorage['acceptTOS']) {
      $('input[name=terms]').attr('checked', 'checked');
    }
    if (getParam('source')) {
      $('input[name=issueURL]').val(getParam('source'));
    }

    $('#submitBounty').click(function(e) {
      mixpanel.track('Claim Bounty Clicked', {});
      loading_button($('#submitBounty'));
      e.preventDefault();
      var fullName = $('input[name=fullName]').val();
      var notificationEmail = $('input[name=notificationEmail]').val();
      var githubUsername = $('input[name=githubUsername]').val();
      var issueURL = $('input[name=issueURL]').val();

      localStorage['githubUsername'] = githubUsername;

      var isError = false;

      if ($('#terms:checked').length == 0) {
        _alert({message: 'Please accept the terms of service.'}, 'warning');
        isError = true;
      } else {
        localStorage['acceptTOS'] = true;
      }
      if (issueURL == '') {
        _alert({ message: 'Please enter a issue URL.' }, 'warning');
        isError = true;
      }
      if (isError) {
        unloading_button($('#submitBounty'));
        return;
      }

      var account = web3.eth.coinbase;
      var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

      ipfs.ipfsApi = IpfsApi({host: 'ipfs.infura.io', port: '5001', protocol: 'https', root: '/api/v0'});
      ipfs.setProvider({ host: 'ipfs.infura.io', port: 5001, protocol: 'https', root: '/api/v0'});

      // https://github.com/ConsenSys/StandardBounties/issues/21
      var ipfsFulfill = {
        payload: {
          description: issueURL,
          sourceFileName: '',
          sourceFileHash: '',
          sourceDirectoryHash: '',
          fulfiller: {
            name: fullName,
            email: notificationEmail,
            githubUsername: githubUsername,
            address: account
          },
          metadata: {}
        },
        meta: {
          platform: 'gitcoin',
          schemaVersion: '0.1',
          schemaName: 'gitcoinFulfillment'
        }
      };

      var _callback = function(error, result) {
        var ignore_error = false;

        if (error) {
          console.error(error);
          mixpanel.track('Fulfill Bounty Error', {step: '_callback', error: error});
          ignore_error = String(error).indexOf('BigNumber') != -1;
        }
        document.ipfsDataHash = result; // Cache IPFS data hash
        var run_main = !error || ignore_error;

        if (error && !ignore_error) {
          _alert({ message: 'Could not get bounty details.' }, 'error');
          unloading_button($('#submitBounty'));
        }
        if (run_main) {
          if (!ignore_error) {
            var web3Callback = function(error, result) {
              var next = function() {

                // setup inter page state
                localStorage[issueURL] = JSON.stringify({
                  'timestamp': timestamp(),
                  'dataHash': null,
                  'issuer': account,
                  'txid': result
                });

                dataLayer.push({'event': 'claimissue'});
                _alert({ message: 'Fulfillment submitted to web3.' }, 'info');
                setTimeout(function() {
                  mixpanel.track('Fulfill Bounty Success', {});
                  document.location.href = '/funding/details?url=' + issueURL;
                }, 1000);

              };

              if (error) {
                mixpanel.track('Fulfill Bounty Error', {step: 'callback', error: error});
                console.error('err', error);
                _alert({ message: 'There was an error' }, 'error');
                unloading_button($('#submitBounty'));
              } else {
                next();
              }
            };

            // Get bountyId from the database
            var uri = '/api/v0.1/bounties/?github_url=' + issueURL;

            $.get(uri, function(results, status) {
              results = sanitizeAPIResults(results);
              result = results[0];
              if (result == null) {
                _alert({ message: 'No active bounty found for this Github URL.' }, 'info');
                unloading_button($('#submitBounty'));
                return;
              }

              var bountyId = result['standard_bounties_id'];

              bounty.fulfillBounty(bountyId, document.ipfsDataHash, {gasPrice: web3.toHex($('#gasPrice').val()) * Math.pow(10, 9)}, web3Callback);
            });
          }
          e.preventDefault();
        }
      }; // _callback

      ipfs.addJson(ipfsFulfill, _callback);
    });
  }, 100);
};
