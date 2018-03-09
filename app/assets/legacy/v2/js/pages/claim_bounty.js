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

    var estimateGas = function(issueURL, fulfiller_metadata, success_callback, failure_calllback, final_callback) {
      var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

      $('#gasLimit').addClass('loading');
      bounty.claimBounty.estimateGas(
        issueURL,
        fulfiller_metadata,
        function(errors, result) {
          $('#gasLimit').removeClass('loading');
          var is_issue_taken = typeof result == 'undefined' || result > 403207;

          if (errors || is_issue_taken) {
            failure_calllback(errors);
            return;
          }
          var gas = Math.round(result * gasMultiplier);
          var gasLimit = Math.round(gas * gasLimitMultiplier);

          success_callback(gas, gasLimit, final_callback);
        });
    };
    // updates recommended metamask settings
    var updateInlineGasEstimate = function() {
      var notificationEmail = $('input[name=notificationEmail]').val();
      var githubUsername = $('input[name=githubUsername]').val();
      var issueURL = $('input[name=issueURL]').val();
      var fulfiller_metadata = JSON.stringify({
        notificationEmail: notificationEmail,
        githubUsername: githubUsername
      });
      var success_callback = function(gas, gasLimit, _) {
        $('#gasLimit').val(gas);
        update_metamask_conf_time_and_cost_estimate();
      };
      var failure_callback = function() {
        $('#gasLimit').val('Unknown');
        update_metamask_conf_time_and_cost_estimate();
      };
      var final_callback = function() {
        // …
      };

      // estimateGas(issueURL, fulfiller_metadata, success_callback, failure_callback, final_callback);
      success_callback(186936, 186936, '');
    };

    setTimeout(function() {
      updateInlineGasEstimate();
    }, 100);
    $('input').change(updateInlineGasEstimate);
    $('#gasPrice').keyup(update_metamask_conf_time_and_cost_estimate);


    $('#submitBounty').click(function(e) {
      mixpanel.track('Claim Bounty Clicked', {});
      loading_button($('#submitBounty'));
      e.preventDefault();
      var notificationEmail = $('input[name=notificationEmail]').val();
      var githubUsername = $('input[name=githubUsername]').val();
      var issueURL = $('input[name=issueURL]').val();
      var fulfiller_metadata = JSON.stringify({
        notificationEmail: notificationEmail,
        githubUsername: githubUsername
      });

      localStorage['githubUsername'] = githubUsername;

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

      var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

      var _callback = function(error, result) {
        var ignore_error = false;

        if (error) {
          console.error(error);
          mixpanel.track('Claim Bounty Error', {step: '_callback', error: error});
          ignore_error = String(error).indexOf('BigNumber') != -1;
        }
        var run_main = !error || ignore_error;

        if (error && !ignore_error) {
          _alert({ message: 'Could not get bounty details.' });
          unloading_button($('#submitBounty'));
        }
        if (run_main) {
          if (!ignore_error) {
            var bountyAmount = result[0].toNumber();

            bountyDetails = [ bountyAmount, result[1], result[2], result[3] ];
            var fromAddress = result[2];
            var claimeeAddress = result[3];
            var open = result[4];
            var initialized = result[5];

            var errormsg = undefined;

            if (bountyAmount == 0 || open == false || initialized == false) {
              errormsg = 'No active bounty found at this address.  Are you sure this is an active bounty?';
            }

            if (errormsg) {
              _alert({ message: errormsg });
              unloading_button($('#submitBounty'));
              return;
            }
          }


          var final_callback = function(error, result) {
            var next = function() {
              localStorage['txid'] = result;
              dataLayer.push({'event': 'claimissue'});
              sync_web3(issueURL);
              localStorage[issueURL] = timestamp();
              _alert({ message: 'Claim submitted to web3.' }, 'info');
              setTimeout(function() {
                mixpanel.track('Claim Bounty Success', {});
                document.location.href = '/funding/details?url=' + issueURL;
              }, 1000);

            };

            if (error) {
              mixpanel.track('Claim Bounty Error', {step: 'callback', error: error});
              console.error('err', error);
              _alert({ message: 'There was an error' });
              unloading_button($('#submitBounty'));
            } else {
              next();
            }
          };

          setTimeout(function() {
            var failure_calllback = function(errors) {
              _alert({ message: 'This issue is no longer active.  Please leave a comment <a href=https://github.com/gitcoinco/web/issues/169>here</a> if you need help.' });
              console.log(errors);
              mixpanel.track('Claim Bounty Error', {step: 'estimateGas', error: errors});
              unloading_button($('#submitBounty'));
              return;
            };
            var success_callback = function(gas, gasLimit, final_callback) {
              var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

              bounty.claimBounty.sendTransaction(issueURL,
                fulfiller_metadata,
                {
                  from: account,
                  gas: web3.toHex(gas),
                  gasLimit: web3.toHex(gasLimit),
                  gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
                },
                final_callback);
            };
            // var final_callback = function(){};
            // estimateGas(issueURL, fulfiller_metadata, success_callback, failure_calllback, final_callback);

            bounty.claimBounty.estimateGas(
              issueURL,
              fulfiller_metadata,
              function(errors, result) {
                var is_issue_taken = typeof result == 'undefined' || result > 403207;

                if (errors || is_issue_taken) {
                  failure_calllback(errors);
                  return;
                }
                var gas = Math.round(result * gasMultiplier);
                var gasLimit = Math.round(gas * gasLimitMultiplier);

                success_callback(gas, gasLimit, final_callback);
              });
          }, 100);
          e.preventDefault();
        }
      };

      bounty.bountydetails.call(issueURL, _callback);
    });
  }, 100);
};
