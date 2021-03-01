/**
 * Handles Bounty Cancellation for bounties funded in ETH/ERC20 tokens
 * Data is stored on IPFS + the data is stored in
 * standard bounties contract on the ethereum blockchain
 */
const ethCancelBounty = data => {

  if (is_bounties_network) {
    waitforWeb3(actions_page_warn_if_not_on_same_network);
  }

  try {
    bounty_address();
  } catch (exception) {
    _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
    return;
  }

  const params = data.payload;

  const sendForm = fetchData('cancel_reason', 'POST', params);

  $.when(sendForm).then(function(payback) {
    return payback;
  });

  loading_button($('.js-submit'));
  const issueURL = data.issueURL;

  let bounty = new web3.eth.Contract(bounty_abi, bounty_address());

  const apiCallback = function(results, status) {
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
    }

    if (fromAddress.toLowerCase() != selectedAccount.toLowerCase()) {
      errormsg = gettext(
        'Only the address that submitted this funded issue may kill the bounty.'
      );
    }

    if (errormsg) {
      _alert({ message: errormsg });
      unloading_button($('.js-submit'));
      return;
    }

    const final_callback = function(result, error) {
      indicateMetamaskPopup(true);
      const next = function() {
        // setup inter page state
        localStorage[issueURL] = JSON.stringify({
          timestamp: timestamp(),
          dataHash: null,
          issuer: selectedAccount,
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

    bounty.methods.killBounty(bountyId).send({
      from: selectedAccount
    }).then((result) => {
      final_callback(result);
    }).catch(err => {
      final_callback(undefined, err);
      console.log(err);
    });
  };

  const uri = '/api/v0.1/bounties/?event_tag=all&github_url=' +
    issueURL + '&network=' + $('input[name=network]').val() +
    '&standard_bounties_id=' + $('input[name=standard_bounties_id]').val();

  $.get(uri, apiCallback);
};
