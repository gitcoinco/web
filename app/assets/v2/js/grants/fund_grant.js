/* eslint-disable no-console */
window.onload = function() {

  let token = '0x0000000000000000000000000000000000000000';

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
      };

      console.log(grant);


      let value = 0;
      let txData = '0x02'; // something like this to say, hardcoded VERSION 2, we're sending approved tokens
      let gasLimit = 120000;

      // hardcode period seconds to monthly
      let periodSeconds = 2592000;

      if (!data.gas_price)
        data.gas_price = 0;

      let SubscriptionContract = web3.eth.contract(compiledSubscription.abi);

      let deployedSubscription = SubscriptionContract.at(data.contract_address);

      // This token is only for testing
      let TokenContract = web3.eth.contract(compiledToken.abi);

      let deployedToken = TokenContract.at('0x8E66e7eC5d9Fd04410d77142e51fd5c49a2B1263');

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
};
