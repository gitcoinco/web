/* eslint-disable no-console */
window.onload = function() {

  // console.log('web3', web3);
  // console.log('web3', Web3);
  var web3 = new Web3(Web3.givenProvider || "ws://localhost:8546");
 console.log(' not new web3', web3);
 console.log('this is a change');


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

      let grant = {
        id: data.grant_id,
        admin_address: data.admin_address,
        token_address: data.token_address,
        contract_address: data.contract_address
      }

      console.log('this is the grants', grant);


      let value = 0
      let txData = "0x02" //something like this to say, hardcoded VERSION 2, we're sending approved tokens
      let gasLimit = 120000

      //hardcode period seconds to monthly
      let periodSeconds=2592000
      if(!data.gas_price) data.gas_price = 0

    let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, grant.contract_address)


      console.log('delpoyedSubscription', deployedSubscription);

      // // This token is only for testing
      // let TokenContract = web3.eth.contract(compiledToken.abi);
      //
      // let deployedToken = TokenContract.at('0x8E66e7eC5d9Fd04410d77142e51fd5c49a2B1263');
      // //
      let deployedToken = new web3.eth.Contract(compiledToken.abi, '0xa00d98FeaEbD194F94af90fDDa163A34DF5dea89')

      console.log('methods', deployedToken.methods)

      deployedToken.methods.decimals().call(function(err, decimals){

        console.log('decimals', decimals);
      //
      // // console.log(bignumber);
      // let decimalsNumber = decimals.toNumber()

      // //
          let realTokenAmount = data.amount_per_period*10**decimals
          let realGasPrice = data.gas_price*10**decimals

          console.log(realTokenAmount);
          console.log(realGasPrice);

          web3.eth.getAccounts(function(err, accounts){

            console.log(accounts[0]);

          deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce){

             nonce = parseInt(nonce)+1

             console.log("nonce", nonce);

             const parts = [
               accounts[0],
               grant.admin_address,
               grant.token_address,
               web3.utils.toTwosComplement(realTokenAmount),
               web3.utils.toTwosComplement(periodSeconds),
               web3.utils.toTwosComplement(realGasPrice),
               web3.utils.toTwosComplement(nonce)
             ]

             deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash){

               console.log('subscriptionHash', subscriptionHash);

                  web3.eth.personal.sign(""+subscriptionHash, accounts[0], function(err, signature){

                    console.log("signature",signature)
      //
      //
                 let postData = {
                   subscriptionContract: grant.contract_address,
                   parts:parts,
                   subscriptionHash: subscriptionHash,
                   signature:signature,
                 }
      //
      //            console.log("postData",JSON.stringify({
      //              postData
      //            }))
      //
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
// get data from grant and inputs
// getSubscriptionHash from contract_address
// create Signature
// submit Signature
// save data and signature

    }
  })
};
