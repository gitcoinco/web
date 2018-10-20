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
        '0x00e8baC402e187608C6585c435C9D35947770f5B'
      );

      web3.eth.getAccounts(function(err, accounts) {

        deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0], gas: 10 0000}, function(err, result) {

          form.submit();

        });
      });
    }
  });

};
