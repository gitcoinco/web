function saveMatchingPartner(hash) {

};

function processPayment() {

  var transactionParams = {
    to: '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
    from: '0x250608D0AEEB7489Adba2aE5856c80b8714ffABf',
  }

  web3.eth.sendTransaction(
    transactionParams,
    function(error, hash) {
      if (error) {
        _alert(error.message, 'error');
      }
      else {
        saveMatchingPartner(hash);
        _alert(
          'Thank you for volunteering to match on Gitcoin Grants. You are supporting open source, and we thank you',
          'success'
        );
      }
    }
  );
};


