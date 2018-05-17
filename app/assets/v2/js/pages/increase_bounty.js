load_tokens();

// Wait until page is loaded, then run the function
$(document).ready(function() {
  waitforWeb3(actions_page_warn_if_not_on_same_network);
  
  $('input[name=amount]').keyup(setUsdAmount);
  $('input[name=amount]').blur(setUsdAmount);
  $('select[name=deonomination]').change(setUsdAmount);

  $('input[name=amount]').focus();

  var denomSelect = $('select[name=deonomination]');

  localStorage['tokenAddress'] = denomSelect.data('tokenAddress');
  localStorage['amount'] = 0;
  denomSelect.select2();
  $('.js-select2').each(function() {
    $(this).select2();
  });

  // submit bounty button click
  $('#submitBounty').click(function(e) {
    try {
      bounty_address();
    } catch (exception) {
      _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
      return;
    }

    mixpanel.track('Increase Bounty Clicked (funder)', {});

    // setup
    e.preventDefault();
    loading_button($(this));

    var issueURL = $('input[name=issueURL]').val();
    var amount = $('input[name=amount]').val();
    var tokenAddress = $('select[name=deonomination]').val();
    var token = tokenAddressToDetails(tokenAddress);
    var decimals = token['decimals'];
    var tokenName = token['name'];
    var decimalDivisor = Math.pow(10, decimals);

    // validation
    var isError = false;

    if ($('#terms:checked').length == 0) {
      _alert({ message: gettext('Please accept the terms of service.') });
      isError = true;
    } else {
      localStorage['acceptTOS'] = true;
    }
    var is_issueURL_invalid = issueURL == '' ||
        issueURL.indexOf('http') != 0 ||
        issueURL.indexOf('github') == -1 ||
        issueURL.indexOf('javascript:') != -1

    ;
    if (is_issueURL_invalid) {
      _alert({ message: gettext('Please enter a valid github issue URL.') });
      isError = true;
    }
    if (amount == '') {
      _alert({ message: gettext('Please enter an amount.') });
      isError = true;
    }
    if (isError) {
      unloading_button($(this));
      return;
    }
    $(this).attr('disabled', 'disabled');

    // setup web3
    // TODO: web3 is using the web3.js file.  In the future we will move
    // to the node.js package.  github.com/ethereum/web3.js
    var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
    var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
    var account = web3.eth.coinbase;

    amount = amount * decimalDivisor;
    // Create the bounty object.
    // This function instantiates a contract from the existing deployed Standard Bounties Contract.
    // bounty_abi is a giant object containing the different network options
    // bounty_address() is a function that looks up the name of the network and returns the hash code
    var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

    // setup inter page state
    localStorage[issueURL] = JSON.stringify({
      'timestamp': null,
      'txid': null
    });

    function web3Callback(error, result) {
      if (error) {
        mixpanel.track('Increase Bounty Error (funder)', {step: 'post_bounty', error: error});
        _alert({ message: gettext('There was an error.  Please try again or contact support.') });
        unloading_button($('#submitBounty'));
        return;
      }

      // update localStorage issuePackage
      var issuePackage = JSON.parse(localStorage[issueURL]);

      issuePackage['txid'] = result;
      issuePackage['timestamp'] = timestamp();
      localStorage[issueURL] = JSON.stringify(issuePackage);

      _alert({ message: gettext('Submission sent to web3.') }, 'info');
      setTimeout(function() {
        mixpanel.track('Submit New Bounty Success', {});
        document.location.href = '/funding/details/?url=' + issueURL;
      }, 1000);
    }

    var bountyAmount = parseInt($('input[name=valueInToken]').val(), 10);
    var ethAmount = isETH ? amount : 0;
    var bountyId = $('input[name=standardBountiesId]').val();
    var fromAddress = $('input[name=bountyOwnerAddress]').val();

    var errormsg = undefined;

    if (bountyAmount == 0 || open == false) {
      errormsg = gettext('No active funded issue found at this address on ' + document.web3network + '. Are you sure this is an active funded issue?');
    }
    if (fromAddress != web3.eth.coinbase) {
      errormsg = gettext('Only the address that submitted this funded issue may increase the payout.');
    }

    if (errormsg) {
      _alert({ message: errormsg });
      unloading_button($('#submitBounty'));
      return;
    }

    function approveSuccessCallback() {
      bounty.increasePayout(
        bountyId,
        bountyAmount + amount,
        amount,
        {
          from: account,
          value: ethAmount,
          gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
        },
        web3Callback
      );
    }

    if (isETH) {
      // no approvals needed for ETH
      approveSuccessCallback();
    } else {
      token_contract.approve(
        bounty_address(),
        amount,
        {
          from: account,
          value: 0,
          gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
        },
        approveSuccessCallback
      );
    }
  });
});
