/* eslint-disable no-console */
window.onload = function() {
  $('#period').select2();


  $('#js-cancelSubscription').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      // currently practically cancelled, but need to delete subscription from miner so it isn't checked every 15 seconds.

      let deployedToken = new web3.eth.Contract(
        compiledToken.abi,
        // data.token_address
        '0xFD9C55bf4B75Ef115749cF76E9083c4241D7a7eB'
      );

      web3.eth.getAccounts(function(err, accounts) {

        deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0], gas: 50000}, function(err, result) {

          form.submit();

        });
      });
    }
  });

};
