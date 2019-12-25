/* eslint-disable no-console */
window.onload = function() {
  // a little time for web3 injection
  setTimeout(function() {
    waitforWeb3(actions_page_warn_if_not_on_same_network);
    var account = web3.eth.accounts[0];

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
          if (this.value) {
            data[this.name] = this.value;
          }
        });

        const selectedRadio = $('input[name=canceled_bounty_reason]:checked').val();
        let reasonCancel;

        if (selectedRadio == 'other') {
          reasonCancel = $('#reason_text').val();
        } else {
          reasonCancel = selectedRadio;
        }
        const payload = {
          pk: $('input[name=pk]').val(),
          canceled_bounty_reason: reasonCancel
        };

        const sendForm = fetchData('cancel_reason', 'POST', payload);

        $.when(sendForm).then(function(payback) {
          return payback;
        });


        disabled.attr('disabled', 'disabled');

        loading_button($('.js-submit'));
        const issueURL = data.issueURL;

        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

        var apiCallback = function(results, status) {
          if (status != 'success') {
            _alert({ message: gettext('Could not get bounty details') });
            console.error(error);
            unloading_button($('.submitBounty'));
            return;
          }
          results = sanitizeAPIResults(results);
          result = results[0];
          if (result == null) {
            _alert({
              message: gettext('No active bounty found for this Github URL on ' + document.web3network + '.')
            });
            unloading_button($('.js-submit'));
            return;
          }

          const bountyAmount = parseInt(result['value_in_token'], 10);
          const fromAddress = result['bounty_owner_address'];
          const is_open = result['is_open'];
          const bountyId = result['standard_bounties_id'];

          let errormsg = undefined;

          if (bountyAmount > 0 && !is_open) {
            errormsg = gettext(
              'This bounty is already in progress, canceling the issue is no longer possible.'
            );
          } else if (bountyAmount == 0 || is_open == false) {
            errormsg = gettext(
              'No active funded issue found at this address.  Are you sure this is an active funded issue?'
            );
          } else if (fromAddress != web3.eth.coinbase) {
            errormsg = gettext(
              'Only the address that submitted this funded issue may kill the bounty.'
            );
          }

          if (errormsg) {
            _alert({ message: errormsg });
            unloading_button($('.js-submit'));
            return;
          }

          var final_callback = function(error, result) {
            indicateMetamaskPopup(true);
            var next = function() {
              // setup inter page state
              localStorage[issueURL] = JSON.stringify({
                timestamp: timestamp(),
                dataHash: null,
                issuer: account,
                txid: result
              });

              _alert({ message: gettext('Cancel bounty submitted to web3.') }, 'info');
              setTimeout(() => {
                document.location.href = '/funding/details/?url=' + issueURL;
              }, 1000);
            };

            if (error) {
              console.error('err', error);
              _alert({ message: gettext('There was an error') });
              unloading_button($('.js-submit'));
            } else {
              next();
            }
          };

          indicateMetamaskPopup();
          bounty.killBounty(
            bountyId,
            { gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9)) },
            final_callback
          );

        };
        // Get bountyId from the database
        var uri = '/api/v0.1/bounties/?event_tag=all&github_url=' + issueURL + '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' + $('input[name=standard_bounties_id]').val();

        $.get(uri, apiCallback);
      }
    });
  }, 100);
};
