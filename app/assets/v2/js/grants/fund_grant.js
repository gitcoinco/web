/* eslint-disable no-console */
window.onload = function() {

  alert("Just so you know, you will perform two actions in MetaMask on this page!")

  // this variable acts as a placeholder for testing
  let token = '0x0000000000000000000000000000000000000000'

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
      let deployedToken = new web3.eth.Contract(compiledToken.abi, '0xfC3FeB6064fe0CBcd675Ec4DD4b5c07C84f3CfC0')


      deployedToken.methods.decimals().call(function(err, decimals){

        console.log('decimals', typeof decimals);

      let realTokenAmount = Number(data.amount_per_period*10**decimals)
      console.log('realTokenAmount', realTokenAmount);

      let realGasPrice = Number(data.gas_price*10**decimals)

        web3.eth.getAccounts(function(err, accounts){

          console.log('accounts', accounts);

          $('#contributor_address').val(accounts[0])

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(realTokenAmount)).send({from: accounts[0]}, function(err, result){

            // Should add approval transactions to transaction history
            console.log('result', result);

              deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce){

                console.log('nonce1', nonce);

                nonce = parseInt(nonce)+1

                console.log('nonce', nonce);

                const parts = [
                  accounts[0],
                  data.admin_address,
                  '0xfC3FeB6064fe0CBcd675Ec4DD4b5c07C84f3CfC0',
                  web3.utils.toTwosComplement(realTokenAmount),
                  web3.utils.toTwosComplement(periodSeconds),
                  web3.utils.toTwosComplement(realGasPrice),
                  web3.utils.toTwosComplement(nonce)
                ]

                console.log('parts', parts);

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
      })


// instantiate contract
// get data from data and inputs
// getSubscriptionHash from contract_address
// create Signature
// submit Signature
// save data and signature

    }
  })

};
