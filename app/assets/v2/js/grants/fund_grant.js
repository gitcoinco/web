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

      let realPeriodSeconds = 0;

      if (data.frequency) {
        // translate timeAmount&timeType to requiredPeriodSeconds
        let periodSeconds = data.frequency;

        if (data.frequency_unit == 'minutes') {
          periodSeconds *= 60;
        } else if (data.frequency_unit == 'hours') {
          periodSeconds *= 3600;
        } else if (data.frequency_unit == 'days') {
          periodSeconds *= 86400;
        } else if (data.frequency_unit == 'months') {
          periodSeconds *= 2592000;
        }
        if (periodSeconds) {
          realPeriodSeconds = periodSeconds;
        }
      }

      if (!data.gas_price)
        data.gas_price = 0;

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      // This token is only for testing
      // will need to make dynamic with data.token_address
      let deployedToken = new web3.eth.Contract(compiledToken.abi, '0x00e8baC402e187608C6585c435C9D35947770f5B');

      deployedToken.methods.decimals().call(function(err, decimals) {

        console.log('decimals', decimals);

        let realApproval = Number(data.approve * 10 ** decimals);

        console.log('realApproval', realApproval);

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);

        console.log('realTokenAmount', realTokenAmount);

        let realGasPrice = Number(data.gas_price * 10 ** decimals);

        console.log('realGasPrice', realGasPrice);

        web3.eth.getAccounts(function(err, accounts) {

          console.log('accounts', accounts);

          $('#contributor_address').val(accounts[0]);

          // need to figure out why there does not seem to be a limit to this amount. Probably setting way higher than thought

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(realApproval)).send({from: accounts[0]}, function(err, result) {

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
                '0x00e8baC402e187608C6585c435C9D35947770f5B',
                // data.amount_per_period
                web3.utils.toTwosComplement(realTokenAmount),
                // data.period_seconds
                web3.utils.toTwosComplement(realPeriodSeconds),
                // data.gas_price
                web3.utils.toTwosComplement(realGasPrice),
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

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      let option = document.createElement('option');

      option.text = ele.name;
      option.value = ele.addr;

      $('#js-token').append($('<option>', {
        value: ele.addr,
        text: ele.name
      }));
    });
    $('#js-token').select2();
  });
});
