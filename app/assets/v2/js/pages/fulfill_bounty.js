/* eslint-disable no-console */
window.onload = function() {

  // Check Radio-box
  $('.rating input:radio').attr('checked', false);

  $('.rating input').click(function() {
    $('.rating span').removeClass('checked');
    $(this).parent().addClass('checked');
  });

  $('input:radio').change(
    function() {
      var userRating = this.value;
    });

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

        ipfs.ipfsApi = IpfsApi(ipfsConfig);
        ipfs.setProvider(ipfsConfig);

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
                indicateMetamaskPopup(true);
                var next = function() {
                  // setup inter page state
                  localStorage[issueURL] = JSON.stringify({
                    timestamp: timestamp(),
                    dataHash: null,
                    issuer: account,
                    txid: result
                  });

                  var finishedComment = function() {
                    dataLayer.push({ event: 'claimissue' });
                    _alert({ message: gettext('Fulfillment submitted to web3.') }, 'info');
                    setTimeout(() => {
                      document.location.href = '/funding/details?url=' + issueURL;
                    }, 1000);
                  };

                  finishedComment();
                };

                if (error) {
                  console.error('err', error);
                  _alert({ message: gettext('There was an error') });
                  unloading_button($('.js-submit'));
                } else {
                  next();
                }
              };

              // Get bountyId from the database
              var uri = '/api/v0.1/bounties/?event_tag=all&github_url=' + issueURL + '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' + $('input[name=standard_bounties_id]').val();

              $.get(uri, function(results, status) {
                results = sanitizeAPIResults(results);
                result = results[0];
                if (result == null) {
                  _alert({
                    message: 'No active bounty found for this Github URL.'
                  });
                  unloading_button($('.js-submit'));
                  return;
                }

                var bountyId = result['standard_bounties_id'];

                indicateMetamaskPopup();
                bounty.fulfillBounty(
                  bountyId,
                  document.ipfsDataHash,
                  {
                    gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
                  },
                  web3Callback
                );
              });
            }
          }
        }; // _callback

        ipfs.addJson(ipfsFulfill, _callback);
      }
    });
  }, 100);
};
