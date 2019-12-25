const GITCOIN_ADDRESS = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';

function createMatchingPartner(transactionID, transactionAmount) {
  let newMatchPledgeUrl = '/grants/matching-partners/new';

  $.post(newMatchPledgeUrl, {hash: transactionID, amount: transactionAmount}).then(function(result) {
    _alert(
      result.message,
      'success'
    );
  }).fail(function(data) {
    _alert(
      data.responseJSON['message'],
      'error'
    );
  });
}

function saveTransactionDetails(transactionID) {

  web3.eth.getTransaction(transactionID).then(function(transactionDetails) {
    let network = document.web3network || 'mainnet';
    let data = {
      'txid': transactionID,
      'amount': transactionDetails.value,
      'network': network,
      'from_address': transactionDetails.from,
      'to_address': transactionDetails.to,
      'type': 'matchpledge'
    };

    let newAttestationsUrl = '/revenue/attestations/new';

    setTimeout(function() {
      $.post(newAttestationsUrl, data).then(function(result) {
        createMatchingPartner(transactionID, transactionDetails.value);
      });
    }, 1000);

  });

}

function processPayment() {
  var ethAmount = prompt('How many ETH would you like to transfer?', '1ETH');

  if (ethAmount && ethAmount.length > 0) {
    ethAmount = ethAmount.replace('ETH', '');
    if (isNaN(ethAmount) === true) {
      _alert('Please provide correct amount.', 'error');
      return;
    }
    var transactionParams = {
      to: GITCOIN_ADDRESS,
      from: web3.currentProvider.selectedAddress,
      value: web3.utils.toWei(ethAmount)
    };

    indicateMetamaskPopup();
    web3.eth.sendTransaction(
      transactionParams,
      function(error, hash) {
        if (error) {
          _alert(error.message, 'error');
        } else {
          indicateMetamaskPopup(true);
          _alert('Please wait for this tx to confirm.', 'info');
          saveTransactionDetails(hash);
        }
      }
    );
  }
}
