/* eslint-disable no-console */
window.onload = function() {

  const rateUser = () => {
    if ($('#bountyFulfillment').select2('data')[0]) {
      let userSelected = $('#bountyFulfillment').select2('data')[0].text;

      $('[data-open-rating]').data('openUsername', userSelected.trim());
    }
  };

  $('#bountyFulfillment').on('select2:select', event => {
    rateUser();
  });

  $('.rating input:radio').attr('checked', false);

  $('.rating input').click(function() {
    $('.rating span').removeClass('checked');
    $(this).parent().addClass('checked');
  });

  $('input:radio').change(
    function() {
      var userRating = this.value;
    }
  );

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
      const bounty_amount = parseFloat(document.bounty_amount_whole);
      const pct = parseFloat($(this).val()) * 0.01;
      const estimate = Math.round(bounty_amount * pct * 10 ** 3) / 10 ** 3;

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

    const issueURL = $('input[name=issueURL]').val();
    const contract_version = $('input[name=contract_version]').val();

    waitforWeb3(function() {
      const uri = '/api/v0.1/bounties/?github_url=' + issueURL + '&network=' + document.web3network;

      $.get(uri, fulfillmentCallback);
    });

    $('#goBack').on('click', function(e) {
      const url = window.location.href;
      const new_url = url.replace('process?source', 'details?url');

      window.location.href = new_url;
    });

    var attach_and_send_tip = function(callback) {
      const bounty_amount = parseFloat(document.bounty_amount_whole);
      const pct = parseFloat($('#tipPercent').val()) * 0.01;

      let email = '';
      const github_url = $('#issueURL').val();
      const from_name = document.contxt['github_handle'];
      const username = getSelectedFulfillment() && getSelectedFulfillment().getAttribute('username');
      const amountInEth = bounty_amount * pct;
      let comments_priv = '';
      let comments_public = '';
      let from_email = '';
      const accept_tos = true;
      const tokenAddress = document.token_address;
      const expires = 9999999999;

      var success_callback = function(txid) {
        const url = 'https://' + etherscanDomain() + '/tx/' + txid;
        const msg = 'The tip has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        _alert(msg, 'info');
        callback();
      };

      var failure_callback = function() {
        unloading_button($('.submitBounty'));
      };

      indicateMetamaskPopup();
      return sendTip(
        email,
        github_url,
        from_name,
        username,
        amountInEth,
        comments_public,
        comments_priv,
        from_email,
        accept_tos,
        tokenAddress,
        expires,
        success_callback,
        failure_callback,
        false
      );
    };

    var attach_and_send_kudos = function(selected_kudos, callback) {

      let email = '';
      const github_url = $('#issueURL').val();
      var from_name = document.contxt['github_handle'];
      var username = getSelectedFulfillment() && getSelectedFulfillment().getAttribute('username');
      var amountInEth = selected_kudos.price_finney / 1000.0;
      const comments_public = $('.kudos-comment textarea').val();
      let comments_priv = '';
      var from_email = '';
      const accept_tos = true;
      const to_eth_address = $('#bountyFulfillment option:selected').data('address');
      const expires = 9999999999;
      const kudosId = selected_kudos.id;
      const tokenId = selected_kudos.token_id;
      const send_type = 'github';

      var success_callback = function(txid) {
        const url = 'https://' + etherscanDomain() + '/tx/' + txid;
        const msg = 'The Kudos has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        _alert(msg, 'info');
        callback();
      };

      var failure_callback = function() {
        unloading_button($('.submitBounty'));
      };

      indicateMetamaskPopup();
      return sendKudos(
        email,
        github_url,
        from_name,
        username,
        amountInEth,
        comments_public,
        comments_priv,
        from_email,
        accept_tos,
        to_eth_address,
        expires,
        kudosId,
        tokenId,
        success_callback,
        failure_callback,
        true,
        send_type
      );
    };


    $('#acceptBounty').on('click', function(e) {
      try {
        bounty_address(contract_version);
      } catch (exception) {
        _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
        return;
      }

      e.preventDefault();
      var issueURL = $('input[name=issueURL]').val();
      var fulfillmentId = getSelectedFulfillment() && getSelectedFulfillment().getAttribute('value');

      sessionStorage['bountyId'] = getURLParams('pk');

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

      let bounty = web3.eth.contract(
        getBountyABI(contract_version)).
        at(bounty_address(contract_version)
        );

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

        const bountyAmount = parseInt(result['value_in_token'], 10);
        const fromAddress = result['bounty_owner_address'];
        const claimeeAddress = result['fulfiller_address'];
        const open = result['is_open'];
        const bountyId = result['standard_bounties_id'];

        let errormsg = undefined;

        if (bountyAmount == 0 || open == false) {
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

        var send_payout = function() {
          const gas_price = web3.toHex($('#gasPrice').val() * Math.pow(10, 9));

          indicateMetamaskPopup();

          switch (contract_version) {
            case '2':
              // TODO: std_bounties_2_contract
              console.log('invoke std bounties contract');
              break;
            case '1':
              bounty.acceptFulfillment(
                bountyId,
                fulfillmentId,
                { gasPrice: gas_price },
                final_callback
              );
              break;
          }
        };

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

      waitforWeb3(function() {
        const uri = '/api/v0.1/bounties/?event_tag=all&github_url=' + issueURL +
          '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' +
          $('input[name=standard_bounties_id]').val();

        $.get(uri, apiCallback);
      });
      e.preventDefault();
    });

    function getSelectedFulfillment() {
      return $('#bountyFulfillment').select2('data')[0] ? $('#bountyFulfillment').select2('data')[0].element : null;
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
