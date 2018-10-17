/* eslint-disable no-console */
$(document).ready(function() {

  $('#period').select2();

  $('.js-select2').each(function() {
    $(this).select2();
  });

  // alert("Just so you know, you will perform two actions in MetaMask on this page!")

  $('#js-fundGrant').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      console.log(data);

      let value = 0;
      let txData = '0x02'; // something like this to say, hardcoded VERSION 2, we're sending approved tokens
      let gasLimit = 120000;

      // hardcode period seconds to monthly
      let periodSeconds = 60;

      if (!data.gas_price)
        data.gas_price = 0;


      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      // This token is only for testing
      let deployedToken = new web3.eth.Contract(compiledToken.abi, '0xFD9C55bf4B75Ef115749cF76E9083c4241D7a7eB');


      deployedToken.methods.decimals().call(function(err, decimals) {

        console.log('decimals', typeof decimals);

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);

        console.log('realTokenAmount', realTokenAmount);

        let realGasPrice = Number(data.gas_price * 10 ** decimals);


        web3.eth.getAccounts(function(err, accounts) {

          console.log('accounts', accounts);

          $('#contributor_address').val(accounts[0]);

          // need to figure out why there does not seem to be a limit to this amount. Probably setting way higher than thought

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(realTokenAmount)).send({from: accounts[0]}, function(err, result) {

            // Should add approval transactions to transaction history
            console.log('result', result);


            deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

              console.log('nonce1', nonce);

              nonce = parseInt(nonce) + 1;

              console.log('nonce', nonce);

              const parts = [
                // subscriber address
                accounts[0],
                // admin_address
                data.admin_address,
                // testing token
                '0xFD9C55bf4B75Ef115749cF76E9083c4241D7a7eB',
                // data.amount_per_period
                web3.utils.toTwosComplement(data.amount_per_period),
                // data.period_seconds
                web3.utils.toTwosComplement(60),
                // data.gas_price
                web3.utils.toTwosComplement(data.gas_price),
                // nonce
                web3.utils.toTwosComplement(nonce)
              ];

              console.log('parts', parts);


              deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash) {

                $('#subscription_hash').val(subscriptionHash);


                web3.eth.personal.sign('' + subscriptionHash, accounts[0], function(err, signature) {

                  $('#signature').val(signature);

                  let postData = {
                    subscriptionContract: data.contract_address,
                    parts: parts,
                    subscriptionHash: subscriptionHash,
                    signature: signature
                  };

                  console.log('postData', postData);

                  fetch('http://localhost:10003/saveSubscription', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                      postData
                    })
                  }).then((response)=>{
                    console.log('TX RESULT', response);

                    $.each($(form).serializeArray(), function() {
                      data[this.name] = this.value;
                    });

                    console.log('data', data);

                    form.submit();

                  })
                    .catch((error)=>{
                      console.log(error);
                    });


                });
              });
            });

          });


        });
      });

    }
  });

});

// will want to check if account already has a subscription. If a second is produced the timestamp will not function properly
// will need to check network to make sure users aren't submiting transactions to non-existant contracts
