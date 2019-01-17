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

          let url;

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(0)).send({from: accounts[0], gasPrice: realGasPrice})
            .on('transactionHash', function(transactionHash) {
              $('#sub_end_approve_tx_id').val(transactionHash);
              const linkURL = etherscan_tx_url(transactionHash);

              document.issueURL = linkURL;
              $('#transaction_url').attr('href', linkURL);
              enableWaitState('#grants_form');

              let data = {
                'csrfmiddlewaretoken': $("#js-cancelSubscription input[name='csrfmiddlewaretoken']").val(),
                'sub_end_approve_tx_id': $('#sub_end_approve_tx_id').val()
              };

              $.ajax({
                type: 'post',
                url: '',
                data: data,
                success: json => {
                  console.log('Your approve 0 call successfully saved');
                },
                error: () => {
                  _alert({ message: gettext('Your approve 0 call failed to save. Please try again.') }, 'error');
                  url = window.location;
                }
              });

              deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

                nonce = parseInt(nonce) + 1;

                const parts = [
                  accounts[0], // subscriber address

                  $('#admin_address').val(), // admin_address
                  $('#token_address').val(), // testing token
                  web3.utils.toTwosComplement(amountSTR), // data.amount_per_period
                  web3.utils.toTwosComplement($('#real_period_seconds').val()), // data.period_seconds
                  web3.utils.toTwosComplement(realGasPrice), // data.gas_price
                  web3.utils.toTwosComplement(nonce), // nonce
                  $('#signature').val() // contributor_signature
                ];

                deployedSubscription.methods.cancelSubscription(
                  ...parts
                ).send({from: accounts[0], gasPrice: realGasPrice})
                  .on('transactionHash', function(transactionHash) {
                    $('#sub_cancel_tx_id').val(transactionHash);
                    let data = {
                      'sub_cancel_tx_id': $('#sub_cancel_tx_id').val(),
                      'csrfmiddlewaretoken': $("#js-cancelSubscription input[name='csrfmiddlewaretoken']").val()
                    };

                    $.ajax({
                      type: 'post',
                      url: '',
                      data: data,
                      success: json => {
                        console.log('Cancel subscription successfully saved');
                      },
                      error: () => {
                        _alert({ message: gettext('Your cancel subscription call failed to save. Please try again.') }, 'error');
                        url = window.location;
                      }
                    });
                  }).on('confirmation', function(confirmationNumber, receipt) {

                    let data = {
                      'sub_cancel_confirmed': true,
                      'csrfmiddlewaretoken': $("#js-cancelSubscription input[name='csrfmiddlewaretoken']").val()
                    };

                    $.ajax({
                      type: 'post',
                      url: '',
                      data: data,
                      success: json => {
                        console.log('Cancel subscription successfully confirmed on chain');
                        url = json.url;
                        $('#wait1').val('false');
                      },
                      error: () => {
                        _alert({ message: gettext('Your cancel subscription transaction failed. Please try again.') }, 'error');
                        url = window.location;
                      }
                    });

                    waitforData(() => {
                      document.suppress_loading_leave_code = true;
                      window.location = url;
                    });
                  });
              });
            })
            .on('confirmation', function(confirmationNumber, receipt) {
              let data = {
                'end_approve_tx_confirmed': true,
                'csrfmiddlewaretoken': $("#js-cancelSubscription input[name='csrfmiddlewaretoken']").val()
              };

              $.ajax({
                type: 'post',
                url: '',
                data: data,
                success: json => {
                  console.log('Approve 0 successfully confirmed on chain');
                },
                error: () => {
                  _alert({ message: gettext('Your cancel subscription tranasction failed. Please try again.') }, 'error');
                  url = window.location;
                }
              });

            })
            .on('error', function(err) {
              console.log('err', err);
            });
        });
      });
    }
  });
});

const waitforData = (callback) => {
  if ($('#wait1').val() === 'false') {
    callback();
  } else {
    var wait_callback = () => {
      waitforData(callback);
    };

    setTimeout(wait_callback, 3000);
  }
};
