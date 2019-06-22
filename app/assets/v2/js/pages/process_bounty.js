/* eslint-disable no-console */
window.onload = function() {

  const rateUser = () => {
    let userSelected = $('#bountyFulfillment').select2('data')[0].text;

    $('[data-open-rating]').data('openUsername', userSelected.trim());
  };


  $('#bountyFulfillment').on('select2:select', event => {
    rateUser();
  });

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

    if (getParam('source')) {
      $('input[name=issueURL]').val(getParam('source'));
    }

    $('#tipPercent').change(function() {
      is_valid = $(this).val() > 0 && !isNaN($(this).val());
      if (!is_valid) {
        $(this).val(0);
      }
      var bounty_amount = parseFloat(document.bounty_amount_whole);
      var pct = parseFloat($(this).val()) * 0.01;
      var estimate = Math.round(bounty_amount * pct * 10 ** 3) / 10 ** 3;

      $('#tipEstimate').text(estimate);
    });

    var fulfillmentCallback = function(results, status) {
      if (status != 'success') {
        _alert({ message: gettext('Could not get fulfillment details') }, 'warning');
        console.error(error);
        unloading_button($('.submitBounty'));
        return;
      }
      results = sanitizeAPIResults(results);
      result = results[0];
      if (result === null) {
        _alert({ message: gettext('No bounty fulfillments found for this Github URL.  Please use the advanced payout tool instead.') }, 'warning');
        unloading_button($('.submitBounty'));
        return;
      }

    };

    var issueURL = $('input[name=issueURL]').val();

    waitforWeb3(function() {
      var uri = '/api/v0.1/bounties/?github_url=' + issueURL + '&network=' + document.web3network;

      $.get(uri, fulfillmentCallback);
    });

    $('#goBack').on('click', function(e) {
      var url = window.location.href;
      var new_url = url.replace('process?source', 'details?url');

      window.location.href = new_url;
    });

    var attach_and_send_tip = function(callback) {
      // get form data
      var bounty_amount = parseFloat(document.bounty_amount_whole);
      var pct = parseFloat($('#tipPercent').val()) * 0.01;

      var email = '';
      var github_url = $('#issueURL').val();
      var from_name = document.contxt['github_handle'];
      var username = getSelectedFulfillment().getAttribute('username');
      var amountInEth = bounty_amount * pct;
      var comments_priv = '';
      var comments_public = '';
      var from_email = '';
      var accept_tos = true;
      var tokenAddress = document.token_address;
      var expires = 9999999999;

      var success_callback = function(txid) {
        var url = 'https://' + etherscanDomain() + '/tx/' + txid;
        var msg = 'The tip has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        // send msg to frontend
        _alert(msg, 'info');
        callback();

      };
      var failure_callback = function() {
        unloading_button($('.submitBounty'));
      };

      return sendTip(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, false);

    };

    var attach_and_send_kudos = function(selected_kudos, callback) {
      // get form data

      var email = '';
      var github_url = $('#issueURL').val();
      var from_name = document.contxt['github_handle'];
      var username = getSelectedFulfillment().getAttribute('username');
      var amountInEth = selected_kudos.price_finney / 1000.0;
      var comments_public = $('.kudos-comment textarea').val();
      var comments_priv = '';
      var from_email = '';
      var accept_tos = true;
      var to_eth_address = $('#bountyFulfillment option:selected').data('address');
      var expires = 9999999999;
      var kudosId = selected_kudos.id;
      var tokenId = selected_kudos.token_id;
      var send_type = 'github';
      var success_callback = function(txid) {
        var url = 'https://' + etherscanDomain() + '/tx/' + txid;
        var msg = 'The Kudos has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        // send msg to frontend
        _alert(msg, 'info');
        callback();

      };
      var failure_callback = function() {
        unloading_button($('.submitBounty'));
      };

      return sendKudos(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, to_eth_address, expires, kudosId, tokenId, success_callback, failure_callback, true, send_type);

    };


    $('#acceptBounty').on('click', function(e) {
      try {
        bounty_address();
      } catch (exception) {
        _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
        return;
      }

      e.preventDefault();
      var issueURL = $('input[name=issueURL]').val();
      var fulfillmentId = getSelectedFulfillment().getAttribute('value');

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
          indicateMetamaskPopup();
          var next = function() {
            // setup inter page state
            localStorage[issueURL] = JSON.stringify({
              'timestamp': timestamp(),
              'dataHash': null,
              'issuer': account,
              'txid': result
            });

            _alert({ message: gettext('Submitted transaction to web3, saving comment(s)...') }, 'info');

            var finishedComment = function() {
              _alert({ message: gettext('Submitted transaction to web3.') }, 'info');
              setTimeout(() => {
                document.location.href = '/funding/details?url=' + issueURL;
              }, 1000);
            };

            finishedComment();
          };

          if (error) {
            _alert({ message: gettext('There was an error') }, 'error');
            console.error(error);
            unloading_button($('.submitBounty'));
          } else {
            next();
          }
        };
        // just sent payout
        var send_payout = function() {
          bounty.acceptFulfillment(bountyId, fulfillmentId, {gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))}, final_callback);
        };

        // send both tip and payout
        var send_tip_and_payout_callback = function() {
          indicateMetamaskPopup();
          if ($('#tipPercent').val() > 0) {
            attach_and_send_tip(send_payout);
          } else {
            send_payout();
          }
        };

        if ($('.kudos-search').select2('data')[0].id) {
          attach_and_send_kudos($('.kudos-search').select2('data')[0], send_tip_and_payout_callback);
        } else {
          send_tip_and_payout_callback();
        }

      };
      // Get bountyId from the database

      waitforWeb3(function() {
        var uri = '/api/v0.1/bounties/?event_tag=all&github_url=' + issueURL + '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' + $('input[name=standard_bounties_id]').val();

        $.get(uri, apiCallback);
      });
      e.preventDefault();
    });

    function getSelectedFulfillment() {
      return $('#bountyFulfillment').select2('data')[0].element;
    }

    function renderFulfillment(selected) {
      if (!selected.element) {
        return selected.text;
      }

      let html =
        '<img class="rounded-circle mr-1" src="' +
        selected.element.getAttribute('avatar') +
        '" width="32" height="32">' +
        selected.element.getAttribute('username') +
        '<i class="px-1 font-smallest middle fas fa-circle"></i>' +
        truncate(selected.element.getAttribute('address'), 4);

      return html;
    }

    $('#bountyFulfillment').select2(
      {
        templateSelection: renderFulfillment,
        templateResult: renderFulfillment,
        escapeMarkup: function(markup) {
          return markup;
        }
      }
    );
    rateUser();

  }, 100);
};
