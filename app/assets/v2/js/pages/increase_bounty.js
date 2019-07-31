/* eslint-disable no-lonely-if */
load_tokens();

const FEE_PERCENTAGE = document.FEE_PERCENTAGE / 100.0;

const is_funder = () => {
  if (web3 && web3.eth && web3.coinbase)
    return document.is_funder_github_user_same && $('input[name=bountyOwnerAddress]').val() == web3.eth.coinbase;
  return document.is_funder_github_user_same;
};

$(document).ready(function() {

  if (!is_funder()) {
    $('#total-section').hide();
    $('#fee-section').hide();
  }

  populateBountyTotal();
  waitforWeb3(actions_page_warn_if_not_on_same_network);

  waitforWeb3(function() {
    if (!is_funder()) {
      $('input, select').removeAttr('disabled');
      $('#increase_funding_explainer').html("Your transaction is secured by the Gitcoin's crowdfunding technology on the Ethereum blockchain. Learn more here.");
    }
  });

  $('input[name=amount]').keyup(setUsdAmount);
  $('input[name=amount]').blur(setUsdAmount);
  $('select[name=denomination]').change(setUsdAmount);


  $('input[name=amount]').on('change', function() {
    populateBountyTotal();
  });

  $('input[name=amount]').focus();

  var denomSelect = $('select[name=denomination]');

  localStorage['tokenAddress'] = denomSelect.data('tokenAddress');
  localStorage['amount'] = 0.01;
  denomSelect.select2();
  $('.js-select2').each(function() {
    $(this).select2();
  });

  // submit bounty button click
  $('#increaseFunding').on('click', function(e) {
    try {
      bounty_address();
    } catch (exception) {
      _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
      return;
    }

    // setup
    e.preventDefault();
    loading_button($(this));

    var issueURL = $('input[name=issueURL]').val();
    var amount = $('input[name=amount]').val();
    var tokenAddress = $('select[name=denomination]').val();

    // validation
    var isError = false;

    if ($('#terms:checked').length == 0) {
      _alert({ message: gettext('Please accept the terms of service.') }, 'error');
      isError = true;
    }
    if (amount <= 0) {
      _alert({ message: gettext('Invalid Amount.') }, 'error');
      isError = true;
    }
    var is_issueURL_invalid = issueURL == '' ||
        issueURL.indexOf('http') != 0 ||
        issueURL.indexOf('github') == -1 ||
        issueURL.indexOf('javascript:') != -1

    ;
    if (is_issueURL_invalid) {
      _alert({ message: gettext('Please enter a valid github issue URL.') }, 'error');
      isError = true;
    }
    if (amount == '') {
      _alert({ message: gettext('Please enter an amount.') }, 'error');
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
    var token = tokenAddressToDetails(tokenAddress);
    var decimals = token['decimals'];
    var decimalDivisor = Math.pow(10, decimals);
    var tokenName = token['name'];
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
      indicateMetamaskPopup(true);
      if (error) {
        _alert({ message: gettext('There was an error.  Please try again or contact support.') }, 'error');
        unloading_button($('#increaseFunding'));
        return;
      }

      // update localStorage issuePackage
      var issuePackage = JSON.parse(localStorage[issueURL]);

      issuePackage['txid'] = result;
      issuePackage['timestamp'] = timestamp();
      localStorage[issueURL] = JSON.stringify(issuePackage);

      _alert({ message: gettext('Submission sent to web3.') }, 'info');
      setTimeout(() => {
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

    if (errormsg) {
      _alert({ message: errormsg });
      unloading_button($('#increaseFunding'));
      return;
    }

    function do_as_crowd() {
      // get form data
      var email = '';
      var github_url = $('#issueURL').val();
      var from_name = document.contxt['github_handle'];
      var username = '';
      var amountInEth = amount / decimalDivisor;
      var comments_priv = '';
      var comments_public = '';
      var from_email = '';
      var accept_tos = $('#terms').is(':checked');
      var expires = 9999999999;

      var success_callback = function(txid) {
        var url = 'https://' + etherscanDomain() + '/tx/' + txid;
        var msg = 'This funding increase has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        // send msg to frontend
        _alert(msg, 'info');

        unloading_button($('#increaseFunding'));

        // show green checkmark
        $('#success_container').css('display', 'block');
        $('.row.content').css('display', 'none');

      };

      failure_callback = function() {
        console.log('failed');
      };

      return sendTip(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, true);

    }

    function do_as_funder() {
      bounty.increasePayout(
        bountyId,
        bountyAmount + amount,
        amount,
        {
          from: account,
          value: ethAmount,
          gas: web3.toHex(65269),
          gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
        },
        web3Callback
      );
    }

    var act_as_funder = is_funder();

    if (act_as_funder) {
      const to_address = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
      const gas_price = web3.toHex($('#gasPrice').val() * Math.pow(10, 9));
      const fee = (Number($('#summary-bounty-amount').html()) * FEE_PERCENTAGE).toFixed(4);

      indicateMetamaskPopup();
      if (FEE_PERCENTAGE == 0) {
        do_as_funder();
      } else {
        if (isETH) {
          web3.eth.sendTransaction({
            to: to_address,
            from: web3.eth.coinbase,
            value: web3.toWei(fee, 'ether'),
            gasPrice: gas_price
          }, function(error, txnId) {
            indicateMetamaskPopup(true);
            if (error) {
              _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
            } else {
              // TODO: Save txnId + feeamount to bounty;
              do_as_funder();
            }
          });
        } else {
          const amountInWei = fee * 1.0 * Math.pow(10, token.decimals);
          const token_contract = web3.eth.contract(token_abi).at(tokenAddress);

          token_contract.transfer(to_address, amountInWei, { gasPrice: gas_price }, function(error, txnId) {
            indicateMetamaskPopup(true);
            if (error) {
              _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
            } else {
              // TODO: Save txnId + feeamount to bounty;
              do_as_funder();
            }
          });
        }
      }
    } else {
      do_as_crowd();
    }
  });
});

/**
 * Calculates total amount needed to fund the bounty
 * Bounty Amount + Fee + Featured Bounty
 */
const populateBountyTotal = () => {
  let amount = parseFloat($('input[name=amount]').val());

  if (isNaN(amount)) {
    amount = 0;
  }
  const fee = Number(amount * FEE_PERCENTAGE).toFixed(4);

  $('#summary-bounty-amount').html(amount);
  $('#summary-fee-amount').html(fee);

  const bountyToken = $('#summary-bounty-token').html();
  const bountyAmount = Number($('#summary-bounty-amount').html());
  const bountyFee = Number((bountyAmount * FEE_PERCENTAGE).toFixed(4));
  const totalBounty = Number(bountyAmount + bountyFee).toFixed(4);
  const total = `${totalBounty} ${bountyToken}`;

  $('.fee-percentage').html(FEE_PERCENTAGE * 100);
  $('#fee-amount').html(bountyFee);
  $('#fee-token').html(bountyToken);
  $('#summary-total-amount').html(total);
};
