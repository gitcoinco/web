/* eslint-disable no-console */
window.onload = function() {
  $('#period').select2();


  $('#js-cancelSubscription').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });


    let deployedToken = new web3.eth.Contract(compiledToken.abi,
      // data.token_address
       '0x6760Deb39EcFc70c8261E0CC3550B1099A14f584');

       web3.eth.getAccounts(function(err, accounts) {

         deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0]}, function(err, result) {

           form.submit();

         })
       })


    }
  });

};
