/* eslint-disable no-console */
window.onload = function() {
  $('#period').select2();


  $('#js-cancelSubscription').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      // need to delete subscription from miner so it isn't checked every 15 seconds.

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      let deployedToken = new web3.eth.Contract(
        compiledToken.abi,
        // data.token_address
        '0x00e8baC402e187608C6585c435C9D35947770f5B'
      );

      deployedToken.methods.decimals().call(function(err, decimals) {

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);

        console.log('realTokenAmount', realTokenAmount);

        let realGasPrice = Number(data.gas_price * 10 ** decimals);

        console.log('realGasPrice', realGasPrice);

        web3.eth.getAccounts(function(err, accounts) {

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0]})
            .on('transactionHash', function(hash) {
              console.log('hash', hash);

              deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

                nonce = parseInt(nonce) + 1;

                const parts = [
                // subscriber address
                  accounts[0],
                  // admin_address
                  data.admin_address,
                  // testing token
                  '0x00e8baC402e187608C6585c435C9D35947770f5B',
                  // data.amount_per_period
                  web3.utils.toTwosComplement(realTokenAmount),
                  // data.period_seconds
                  web3.utils.toTwosComplement(60),
                  // data.gas_price
                  web3.utils.toTwosComplement(realGasPrice),
                  // nonce
                  web3.utils.toTwosComplement(1),
                  // contributor_signature
                  data.signature
                ];

                console.log('parts', parts);

                deployedSubscription.methods.cancelSubscription(
                  ...parts
                ).send({from: accounts[0]})
                  .on('confirmation', function(confirmationNumber, receipt) {
                    console.log('receipt', receipt);

                    form.submit();
                  });
              });
            })
            .on('confirmation', function(confirmationNumber, receipt) {
              console.log('receipt', receipt);
            })
            .on('error', function(err) {
              console.log('err', err);
            });
        });
      });
    }
  });

};
