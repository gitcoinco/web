/* eslint-disable no-console */
window.onload = function() {
  // a little time for web3 injection
  setTimeout(function() {
    var account = web3.eth.accounts[0];

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
        var data = {};
        var disabled = $(form)
          .find(':input:disabled')
          .removeAttr('disabled');

        $.each($(form).serializeArray(), function() {
          data[this.name] = this.value;
        });

        disabled.attr('disabled', 'disabled');
        mixpanel.track('Kill Bounty Clicked', {});

        loading_button($('.js-submit'));
        var issueURL = data.issueURL;

        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

        var apiCallback = function(results, status) {
          if (status != 'success') {
            mixpanel.track('Kill Bounty Error', {
              step: 'apiCallback',
              error: error
            });
            _alert({ message: 'Could not get bounty details' });
            console.error(error);
            unloading_button($('.submitBounty'));
            return;
          }
          results = sanitizeAPIResults(results);
          result = results[0];
          if (result == null) {
            _alert({
              message: 'No active bounty found for this Github URL.'
            });
            unloading_button($('.js-submit'));
            return;
          }

          var bountyAmount = parseInt(result['value_in_token'], 10);
          var fromAddress = result['bounty_owner_address'];
          var claimeeAddress = result['fulfiller_address'];
          var open = result['is_open'];
          var initialized = true;
          var bountyId = result['standard_bounties_id'];

          var errormsg = undefined;

          if (bountyAmount == 0 || open == false || initialized == false) {
            errormsg =
                'No active funded issue found at this address.  Are you sure this is an active funded issue?';
          }
          if (fromAddress != web3.eth.coinbase) {
            errormsg =
                'Only the address that submitted this funded issue may kill the bounty.';
          }

          if (errormsg) {
            _alert({ message: errormsg });
            unloading_button($('.js-submit'));
            return;
          }

          var final_callback = function(error, result) {
            var next = function() {
              // setup inter page state
              localStorage[issueURL] = JSON.stringify({
                timestamp: timestamp(),
                dataHash: null,
                issuer: account,
                txid: result
              });

              _alert({ message: 'Kill bounty submitted to web3.' }, 'info');
              setTimeout(function() {
                mixpanel.track('Kill Bounty Success', {});
                document.location.href = '/funding/details?url=' + issueURL;
              }, 1000);
            };

            if (error) {
              mixpanel.track('Kill Bounty Error', {
                step: 'final_callback',
                error: error
              });
              console.error('err', error);
              _alert({ message: 'There was an error' });
              unloading_button($('.js-submit'));
            } else {
              next();
            }
          };

          bounty.killBounty(
            bountyId,
            { gasPrice: web3.toHex($('#gasPrice').val()) * Math.pow(10, 9) },
            final_callback
          );
          
        };
        // Get bountyId from the database
        var uri = '/api/v0.1/bounties/?github_url=' + issueURL;

        $.get(uri, apiCallback);
      }
    });
  }, 100);
};
