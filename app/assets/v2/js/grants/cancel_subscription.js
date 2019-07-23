/* eslint-disable no-console */
$(document).ready(() => {
  $('#period').select2();

  setInterval (() => {
    notifyOwnerAddressMismatch(
      $('#subscriber-handle').val(),
      $('#subscriber-address').val(),
      '#cancel-subscription',
      'Looks like you\'ve funded this grant with ' + $('#subscriber-address').val() + '. Switch to that to take action on your subscription.'
    );
  }, 1000);

  $('#js-cancelSubscription').validate({
    submitHandler: function(form) {
      let data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      // need to delete subscription from miner so it isn't checked every 15 seconds.

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      let deployedToken = new web3.eth.Contract(
        compiledToken.abi,
        data.token_address
      );

      deployedToken.methods.decimals().call(function(err, decimals) {

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);
        let amountSTR = realTokenAmount.toLocaleString('fullwide', { useGrouping: false });

        let realGasPrice = $('#gasPrice').val() * Math.pow(10, 9);

        web3.eth.getAccounts(function(err, accounts) {

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0], gasPrice: realGasPrice})
            .on('transactionHash', function(transactionHash) {
              $('#sub_end_approve_tx_id').val(transactionHash);
              const linkURL = get_etherscan_url(transactionHash);

              document.issueURL = linkURL;
              $('#transaction_url').attr('href', linkURL);
              enableWaitState('#grants_form');

              deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

                nonce = parseInt(nonce) + 1;

                const parts = [
                  accounts[0], // subscriber address
                  data.admin_address, // admin_address
                  data.token_address, // testing token
                  web3.utils.toTwosComplement(amountSTR), // data.amount_per_period
                  web3.utils.toTwosComplement(data.real_period_seconds), // data.period_seconds
                  web3.utils.toTwosComplement(realGasPrice), // data.gas_price
                  web3.utils.toTwosComplement(nonce), // nonce
                  data.signature // contributor_signature
                ];

                deployedSubscription.methods.cancelSubscription(
                  ...parts
                ).send({from: accounts[0], gasPrice: realGasPrice})
                  .on('transactionHash', function(transactionHash) {
                    $('#sub_cancel_tx_id').val(transactionHash);
                  }).on('confirmation', function(confirmationNumber, receipt) {
                    console.log('receipt', receipt);
                    document.suppress_loading_leave_code = true;
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
});