/* eslint-disable no-console */
if (web3_type === 'web3_modal') {
  needWalletConnection();

  const fetchFromWeb3Wallet = () => {
    if (!provider) {
      onConnect();
    }
    $('#payoutAddress').val(selectedAccount);
    $('#payoutAddress').attr('readonly', true);
  };

  window.addEventListener('dataWalletReady', function(e) {
    if (is_bounties_network || web3_type === 'web3_modal') {
      fetchFromWeb3Wallet();
    }
  }, false);
}

var getWalletAddressPlaceholder = function(chainId) {

  switch (chainId) {
    case '1': // ETH
    case '56': // Binance
    case '61': // ETC
      return '0x...';
    case '1995': // NERVOS ...
      return 'ckb...';
    case '50797': // Tezos
      return 'tz1...';
    case '0': // Bitcoin
      return 'bc1...';
    case '270895': // Casper
      return '01...';
    case '1000':// Harmony
      return 'one...';
    case '58':// Polkadot
      return '1...';
    case '59':// Kusama
      return 'C...';
    case '102':// Zilliqa
      return 'zil...';
    case '600': // Filecoin
      return 'f...';
    case '42220': // Celo
      return '0x...';
    case '30': // RSK
      return '0x...';
    case '50': // Xinfin
      return 'xdc...';
    case '1001': // Algorand
      return 'GRUNDTKRXHX...';
    case '1935': // Sia
      return '';
  }

  return '';
};


window.onload = function() {
  $('#payoutAddress').attr('placeholder', getWalletAddressPlaceholder(bountyChainId));

  $('.rating input:radio').attr('checked', false);

  $('.rating input').click(function() {
    $('.rating span').removeClass('checked');
    $(this).parent().addClass('checked');
  });

  if (typeof localStorage['githubUsername'] != 'undefined') {
    if (!$('input[name=githubUsername]').val()) {
      $('input[name=githubUsername]').val(localStorage['githubUsername']);
    }
  }
  if (getParam('source')) {
    $('input[name=issueURL]').val(getParam('source'));
  }

  jQuery.validator.addMethod('cryptoAddress', function(value, element, params) {
    let chainId = params[0];
    let ret = validateWalletAddress(chainId, value);

    return ret;
  }, jQuery.validator.format('Please enter a valid {1} wallet address.'));


  $('#submitBounty').validate({
    rules: {
      payoutAddress: {
        required: true,
        cryptoAddress: [ bountyChainId, tokenName ]
      }
    },
    submitHandler: function(form) {
      loading_button($('.js-submit'));
      let data = {};

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Submit Work', 'click', 'Bounty Hunter');
      }
      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      if (eventTag && !data.projectId) {
        unloading_button($('.js-submit'));
        return _alert('Please add a project first', 'danger');
      }

      if (is_bounties_network) {
        ethFulfillBounty(data);
      } else {
        fulfillBounty(data);
      }
    }
  });
};