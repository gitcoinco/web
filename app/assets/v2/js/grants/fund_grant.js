/* eslint-disable no-console */
window.onload = function() {

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

      console.log('data', data);

      // sendSubscription()

      // form.submit();
    }
  });



  function sendSubscription(grant){

  let SubscriptionContract = web3.eth.contract(compiledSubscription.abi);
  let deployedSubscription = SubscriptionContract.at(grant.contract_address);

  // This token is only for testing
  let TokenContract = web3.eth.contract(compiledToken.abi);
  let deployedToken = TokenContract.at('0xae5F721ee35Ef0dc32B498aC779C2360E6f6C341');
  tokenContract.decimals().call()
    .then(function(decimals){
      console.log("decimals", parseInt(decimals))

    })

let decimals = 2;

  let value = 0
  let txData = "0x02" //something like this to say, hardcoded VERSION 2, we're sending approved tokens
  let gasLimit = 120000

  //hardcode period seconds to monthly
  let periodSeconds=2592000
  if(!gasPrice) gasPrice = 0

 subscriptionContract.extraNonce(account).call()
  .then(function(){
    console.log('nonce', parseInt(nonce)+1);
  })

  let realTokenAmount = data.amount_per_period*10**decimals
  let realGasPrice = data.gas_price*10**decimals

  const parts = [
    web3.eth.accounts[0],
    grant.admin_address,
    grant.token_address,
    realTokenAmount,
    periodSeconds,
    realGasPrice,
    nonce
  ]

  subscriptionContract.getSubscriptionHash(...parts).call()
    .then(function(){
      console.log("subscriptionHash",subscriptionHash)

    })

// instantiate contract
// get data from grant and inputs
// getSubscriptionHash from contract_address
// create Signature
// submit Signature
// save data and signature
  }

};


  // sendSubscription(){
  //   let {toAddress,timeType,tokenAmount,tokenAddress,gasPrice,account,web3} = this.state
  //
  //   let tokenContract = this.state.customContractLoader("WasteCoin",tokenAddress)
  //   let subscriptionContract = this.state.customContractLoader("Subscription",this.state.deployedAddress)
  //
  //   let value = 0
  //   let txData = "0x02" //something like this to say, hardcoded VERSION 2, we're sending approved tokens
  //   let gasLimit = 120000
  //
  //   //hardcode period seconds to monthly
  //   let periodSeconds=2592000
  //   if(!gasPrice) gasPrice = 0
  //
  //   console.log("TOKEN CONTRACT ",tokenContract)
  //   let decimals = parseInt(await tokenContract.decimals().call())
  //   console.log("decimals",decimals)
  //
  //   let nonce = parseInt(await subscriptionContract.extraNonce(account).call())+1
  //
  //   let realTokenAmount = tokenAmount*10**decimals
  //   let realGasPrice = gasPrice*10**decimals
  //   /*
  //   address from, //the subscriber
  //   address to, //the publisher
  //   address tokenAddress, //the token address paid to the publisher
  //   uint256 tokenAmount, //the token amount paid to the publisher
  //   uint256 periodSeconds, //the period in seconds between payments
  //   uint256 gasPrice, //the amount of tokens or eth to pay relayer (0 for free)
  //    */
  //
  //   const parts = [
  //     account,
  //     toAddress,
  //     tokenAddress,
  //     web3.utils.toTwosComplement(realTokenAmount),
  //     web3.utils.toTwosComplement(periodSeconds),
  //     web3.utils.toTwosComplement(realGasPrice),
  //     web3.utils.toTwosComplement(nonce)
  //   ]
  //   /*web3.utils.padLeft("0x"+nonce,64),*/
  //   console.log("PARTS",parts)
  //
  //   const subscriptionHash = await subscriptionContract.getSubscriptionHash(...parts).call()
  //   console.log("subscriptionHash",subscriptionHash)
  //
  //
  //   let signature = await web3.eth.personal.sign(""+subscriptionHash,account)
  //   console.log("signature",signature)
  //   let postData = {
  //     subscriptionContract:this.state.deployedAddress,
  //     parts:parts,
  //     subscriptionHash: subscriptionHash,
  //     signature:signature,
  //   }
  //
  //   console.log("postData",postData)
  //   axios.post(backendUrl+'saveSubscription', postData, {
  //     headers: {
  //         'Content-Type': 'application/json',
  //     }
  //   }).then((response)=>{
  //     console.log("TX RESULT",response.data.subscriptionHash)
  //   })
  //   .catch((error)=>{
  //     console.log(error);
  //   });
  // }
