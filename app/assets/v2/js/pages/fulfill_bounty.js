/* eslint-disable no-console */
window.onload = function() {
  // a little time for web3 injection
  setTimeout(function() {
    waitforWeb3(actions_page_warn_if_not_on_same_network);
    var account = web3.eth.accounts[0];

    if (typeof localStorage['githubUsername'] != 'undefined') {
      if (!$('input[name=githubUsername]').val()) {
        $('input[name=githubUsername]').val(localStorage['githubUsername']);
      }
    }
    if (typeof localStorage['notificationEmail'] != 'undefined') {
      $('input[name=notificationEmail]').val(localStorage['notificationEmail']);
    }
    if (
      typeof localStorage['acceptTOS'] != 'undefined' &&
      localStorage['acceptTOS']
    ) {
      $('input[name=terms]').attr('checked', 'checked');
    }
    if (getParam('source')) {
      $('input[name=issueURL]').val(getParam('source'));
    }

    $('#submitBounty').validate({
      submitHandler: function(form) {
        try {
          bounty_address();
        } catch (exception) {
          _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
          return;
        }

        var data = {};
        var disabled = $(form)
          .find(':input:disabled')
          .removeAttr('disabled');

        $.each($(form).serializeArray(), function() {
          data[this.name] = this.value;
        });

        disabled.attr('disabled', 'disabled');
        mixpanel.track('Claim Bounty Clicked', {});

        // setup
        loading_button($('.js-submit'));
        var githubUsername = data.githubUsername;
        var issueURL = data.issueURL;
        var notificationEmail = data.notificationEmail;
        var githubPRLink = data.githubPRLink;
        var hoursWorked = data.hoursWorked;

        localStorage['githubUsername'] = githubUsername;

        var account = web3.eth.coinbase;
        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

        ipfs.ipfsApi = IpfsApi({
          host: 'ipfs.infura.io',
          port: '5001',
          protocol: 'https',
          root: '/api/v0'
        });
        ipfs.setProvider({
          host: 'ipfs.infura.io',
          port: 5001,
          protocol: 'https',
          root: '/api/v0'
        });

        // https://github.com/ConsenSys/StandardBounties/issues/21
        var ipfsFulfill = {
          payload: {
            description: issueURL,
            sourceFileName: '',
            sourceFileHash: '',
            sourceDirectoryHash: '',
            fulfiller: {
              githubPRLink: githubPRLink,
              hoursWorked: hoursWorked,
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
            mixpanel.track('Fulfill Bounty Error', {
              step: '_callback',
              error: error
            });
            ignore_error = String(error).indexOf('BigNumber') != -1;
          }
          document.ipfsDataHash = result; // Cache IPFS data hash
          var run_main = !error || ignore_error;

          if (error && !ignore_error) {
            _alert({ message: gettext('Could not get bounty details.') });
            unloading_button($('.js-submit'));
          }
          if (run_main) {
            if (!ignore_error) {
              var web3Callback = function(error, result) {
                var next = function() {
                  // setup inter page state
                  localStorage[issueURL] = JSON.stringify({
                    timestamp: timestamp(),
                    dataHash: null,
                    issuer: account,
                    txid: result
                  });

                  dataLayer.push({ event: 'claimissue' });
                  _alert({ message: gettext('Fulfillment submitted to web3.') }, 'info');
                  setTimeout(function() {
                    mixpanel.track('Fulfill Bounty Success', {});
                    document.location.href = '/funding/details?url=' + issueURL;
                  }, 1000);
                };

                if (error) {
                  mixpanel.track('Fulfill Bounty Error', {
                    step: 'callback',
                    error: error
                  });
                  console.error('err', error);
                  _alert({ message: 'There was an error' });
                  unloading_button($('.js-submit'));
                } else {
                  next();
                }
              };

              // Get bountyId from the database
              var uri = '/api/v0.1/bounties/?github_url=' + issueURL + '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' + $('input[name=standard_bounties_id]').val();

              $.get(uri, function(results, status) {
                results = sanitizeAPIResults(results);
                result = results[0];
                if (result == null) {
                  _alert({
                    message: gettext('No active bounty found for this Github URL.')
                  });
                  unloading_button($('.js-submit'));
                  return;
                }

                var bountyId = result['standard_bounties_id'];
                var bountyNetwork = result['network'];

                // before committing to transaction prompt,
                // retrieve bounty owner's address since a
                // creator cannot fulfill their own bounty.
                var fromAddress = result['bounty_owner_address'];

                if (fromAddress == account) {
                  _alert({ message: gettext('The address that funded an issue cannot fulfill it.') }, 'error');
                  unloading_button($('.js-submit'));
                  return;
                }

                browserNetworkIs(bountyNetwork, function(matchingNetworks) {
                  if (!matchingNetworks) {
                    _alert({ message: gettext('Expected browser to be connected to the Ethereum network' +
                      ' that the bounty was deployed to, ie. \'' + bountyNetwork + '\'.') }, 'error');
                    unloading_button($('.js-submit'));
                    return;
                  }

                  bounty.getBounty.call(bountyId, (errStr, bountyParams) => {
                    var curTime = Math.floor(Date.now() / 1000.0);
                    var deadlineTime = bountyParams[1].toNumber();

                    if (bountyParams[4] != bountyStageEnum['Active']) {
                      errStr = 'The bounty for this Github URL is not active.';
                    } else if (deadlineTime < curTime) {
                      errStr = 'The bounty for this Github URL has expired.';
                    }
                    if (errStr) {
                      _alert({ message: errStr });
                      unloading_button($('.js-submit'));
                      return;
                    }

                    // If all tests pass, attempt tx
                    bounty.fulfillBounty(
                      bountyId,
                      document.ipfsDataHash,
                      {
                        gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
                      },
                      web3Callback
                    );
                  });
                });
              });
            }
          }
        }; // _callback

        ipfs.addJson(ipfsFulfill, _callback);
      }
    });
  }, 100);
};
