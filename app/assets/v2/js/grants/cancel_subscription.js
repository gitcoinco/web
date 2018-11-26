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

      let compiledSubscription;

      if (data.contract_version == 0) {
        compiledSubscription = compiledSubscription0;
      }

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      let deployedToken = new web3.eth.Contract(
        compiledToken.abi,
        data.token_address
      );

      deployedToken.methods.decimals().call(function(err, decimals) {

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);

        console.log('realTokenAmount', realTokenAmount);

        // gas price in gwei
        let realGasPrice = Number(data.gas_price * 10 ** 9);

        console.log('realGasPrice', realGasPrice);

        web3.eth.getAccounts(function(err, accounts) {

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0], gasPrice: 4000000000})
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
                  data.token_address,
                  // data.amount_per_period
                  web3.utils.toTwosComplement(realTokenAmount),
                  // data.period_seconds
                  web3.utils.toTwosComplement(data.real_period_seconds),
                  // data.gas_price
                  web3.utils.toTwosComplement(realGasPrice),
                  // nonce
                  web3.utils.toTwosComplement(nonce),
                  // contributor_signature
                  data.signature
                ];

                console.log('parts', parts);

                deployedSubscription.methods.cancelSubscription(
                  ...parts
                ).send({from: accounts[0], gasPrice: 4000000000})
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
