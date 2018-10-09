/* eslint-disable no-console */
window.onload = function() {

<<<<<<< HEAD
  // this variable acts as a placeholder for testing
  let token = '0x0000000000000000000000000000000000000000'
=======
  let token = '0x0000000000000000000000000000000000000000';
>>>>>>> grants

  $('#period').select2();

  $('.js-select2').each(function() {
    $(this).select2();
  });

  $('#js-fundGrant').validate({
    submitHandler: function(form) {
      var action = $(form).attr('action');
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      console.log(data);

      // web3.eth.net.getId(function(err, network){
      //
      //   console.log(network);
      //
      //   if (network != data.network) {
      //     // break
      //   } else {
      //     // continue
      //   }
      //
      // })

      let value = 0;
      let txData = '0x02'; // something like this to say, hardcoded VERSION 2, we're sending approved tokens
      let gasLimit = 120000;

      // hardcode period seconds to monthly
      let periodSeconds = 2592000;

      if (!data.gas_price)
        data.gas_price = 0;


      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address)

      // This token is only for testing
      let deployedToken = new web3.eth.Contract(compiledToken.abi, '0xa00d98FeaEbD194F94af90fDDa163A34DF5dea89')


<<<<<<< HEAD
      deployedToken.methods.decimals().call(function(err, decimals){

          let realTokenAmount = data.amount_per_period*10**decimals
          let realGasPrice = data.gas_price*10**decimals

          web3.eth.getAccounts(function(err, accounts){

            $('#contributor_address').val(accounts[0])

          deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce){

             nonce = parseInt(nonce)+1

             const parts = [
               accounts[0],
               data.admin_address,
               data.token_address,
               web3.utils.toTwosComplement(realTokenAmount),
               web3.utils.toTwosComplement(periodSeconds),
               web3.utils.toTwosComplement(realGasPrice),
               web3.utils.toTwosComplement(nonce)
             ]

             deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash){

               $('#subscription_hash').val(subscriptionHash)

                  web3.eth.personal.sign(""+subscriptionHash, accounts[0], function(err, signature){

                    $('#signature').val(signature)

                 let postData = {
                   subscriptionContract: data.contract_address,
                   parts:parts,
                   subscriptionHash: subscriptionHash,
                   signature:signature,
                 }

                 fetch('http://localhost:10003/saveSubscription', {
                   method: 'POST',
                   headers: {
                     'Content-Type': 'application/json',
                   },
                   body: JSON.stringify({
                     postData
                   })
                 }).then((response)=>{
                   console.log("TX RESULT",response)

                   $.each($(form).serializeArray(), function() {
                     data[this.name] = this.value;
                   });

                   $(form).submit();
                 })
                 .catch((error)=>{
                   console.log(error);
                 });

               })
             })
          })
        })
      })


// instantiate contract
// get data from data and inputs
// getSubscriptionHash from contract_address
// create Signature
// submit Signature
// save data and signature

    }
  })
=======
      deployedToken.decimals.call(function(err, decimals) {

      // console.log(bignumber);
        let decimalsNumber = decimals.toNumber();
        //
        let realTokenAmount = data.amount_per_period * 10 ** decimalsNumber;
        let realGasPrice = data.gas_price * 10 ** decimalsNumber;
        //

        deployedSubscription.extraNonce.call(web3.eth.accounts[0], function(err, nonce) {

          nonce = parseInt(nonce) + 1;

          const parts = [
            web3.eth.accounts[0],
            data.admin_address,
            data.token_address,
            realTokenAmount,
            periodSeconds,
            realGasPrice,
            nonce
          ];

          deployedSubscription.getSubscriptionHash.call(...parts, function(err, subscriptionHash) {

            console.log('subscriptionHash', typeof (subscriptionHash));

            web3.eth.sign(web3.eth.accounts[0], '' + subscriptionHash, function(err, signature) {

              console.log('signature', signature);


              let postData = {
                subscriptionContract: data.contract_address,
                parts: parts,
                subscriptionHash: subscriptionHash,
                signature: signature
              };

              console.log('postData', JSON.stringify({
                postData
              }));

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
              })
                .catch((error)=>{
                  console.log(error);
                });
            });

          });
        });

      });
    }

    // instantiate contract
    // get data from grant and inputs
    // getSubscriptionHash from contract_address
    // create Signature
    // submit Signature
    // save data and signature


  });
>>>>>>> grants
};
