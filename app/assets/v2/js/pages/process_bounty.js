/* eslint-disable no-console */
window.onload = function() {
  // a little time for web3 injection
  setTimeout(function() {
    waitforWeb3(actions_page_warn_if_not_on_same_network);
    var account = web3.eth.accounts[0];

    if (getParam('source')) {
      $('input[name=issueURL]').val(getParam('source'));
    }
    if (typeof localStorage['acceptTOS'] != 'undefined' && localStorage['acceptTOS']) {
      $('input[name=terms]').attr('checked', 'checked');
    }

    var bountyDetails = [];

    var fulfillmentCallback = function(results, status) {
      if (status != 'success') {
        mixpanel.track('Process Bounty Error', {step: 'fulfillmentCallback', error: error});
        _alert({ message: gettext('Could not get fulfillment details') }, 'warning');
        console.error(error);
        unloading_button($('.submitBounty'));
        return;
      }
      results = sanitizeAPIResults(results);
      result = results[0];
      if (result == null) {
        _alert({ message: gettext('No bounty fulfillments found for this Github URL.') }, 'warning');
        unloading_button($('.submitBounty'));
        return;
      }
      $('#bountyFulfillment').html('');
      $('body').append($('<select>').append($('<option>').attr('value', 'bla bla bla')));
      $.each(result['fulfillments'], function(index, value) {
        // option to build each selector-option:
        var option = $('<option>');

        option.attr('value', value.fulfillment_id);
        var short_addr = value.fulfiller_address.slice(0, 7).concat('...');

        option.text('Id: ' + value.fulfillment_id + ',  Username: ' + value.fulfiller_github_username + ',  Address: ' + short_addr);
        $('#bountyFulfillment').append(option);
      });

      if (getParam('id')) {
        selectedFulfillment = getParam('id');
        $('#bountyFulfillment').find('option[value=' + selectedFulfillment + ']').attr('selected', '');
      }

    };

    var issueURL = $('input[name=issueURL]').val();

    waitforWeb3(function() {
      var uri = '/api/v0.1/bounties/?github_url=' + issueURL + '&network=' + document.web3network;

      $.get(uri, fulfillmentCallback);
    });

    $('#goBack').click(function(e) {
      var url = window.location.href;
      var new_url = url.replace('process?source', 'details?url');

      window.location.href = new_url;
    });

    $('#acceptBounty').click(function(e) {
      try {
        bounty_address();
      } catch (exception) {
        _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
        return;
      }

      mixpanel.track('Process Bounty Clicked', {});
      e.preventDefault();
      var whatAction = $(this).html().trim();
      var issueURL = $('input[name=issueURL]').val();
      var fulfillmentId = $('select[name=bountyFulfillment').val();

      console.log(fulfillmentId);

      var isError = false;

      if ($('#terms:checked').length == 0) {
        _alert({ message: gettext('Please accept the terms of service.') }, 'warning');
        isError = true;
      } else {
        localStorage['acceptTOS'] = true;
      }
      if (issueURL == '') {
        _alert({ message: gettext('Please enter a issue URL.') }, 'warning');
        isError = true;
      }
      if (fulfillmentId == null) {
        _alert({ message: gettext('Please enter a fulfillment Id.') }, 'warning');
        isError = true;
      }
      if (isError) {
        return;
      }

      var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

      loading_button($(this));

      var apiCallback = function(results, status) {
        if (status != 'success') {
          mixpanel.track('Process Bounty Error', {step: 'apiCallback', error: error});
          _alert({ message: gettext('Could not get bounty details') }, 'warning');
          console.error(error);
          unloading_button($('.submitBounty'));
          return;
        }
        results = sanitizeAPIResults(results);
        result = results[0];
        if (result == null) {
          _alert({ message: gettext('No active bounty found for this Github URL on ' + document.web3network + '.') }, 'info');
          unloading_button($('.submitBounty'));
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
          errormsg = gettext('No active funding found at this address.  Are you sure this is an active funded issue?');
        } else if (claimeeAddress == '0x0000000000000000000000000000000000000000') {
          errormsg = gettext('No claimee found for this bounty.');
        } else if (fromAddress != web3.eth.coinbase) {
          errormsg = gettext('You can only process a funded issue if you submitted it initially.');
        }

        if (errormsg) {
          _alert({ message: errormsg }, 'error');
          unloading_button($('.submitBounty'));
          return;
        }

        var final_callback = function(error, result) {
          var next = function() {
            // setup inter page state
            localStorage[issueURL] = JSON.stringify({
              'timestamp': timestamp(),
              'dataHash': null,
              'issuer': account,
              'txid': result
            });

            _alert({ message: gettext('Submitted transaction to web3.') }, 'info');
            setTimeout(function() {
              mixpanel.track('Process Bounty Success', {});
              document.location.href = '/funding/details?url=' + issueURL;
            }, 1000);

          };

          if (error) {
            mixpanel.track('Process Bounty Error', {step: 'final_callback', error: error});
            _alert({ message: gettext('There was an error') }, 'error');
            console.error(error);
            unloading_button($('.submitBounty'));
          } else {
            next();
          }
        };

        bounty.acceptFulfillment(bountyId, fulfillmentId, {gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))}, final_callback);

      };
      // Get bountyId from the database

      waitforWeb3(function() {
        var uri = '/api/v0.1/bounties/?github_url=' + issueURL + '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' + $('input[name=standard_bounties_id]').val();

        $.get(uri, apiCallback);
      });
      e.preventDefault();
    });
  }, 100);

};
