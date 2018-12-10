/* eslint-disable no-console */
$(document).ready(function() {

  $('.js-select2').each(function() {
    $(this).select2();
  });

  $('.select2-selection__rendered').hover(function() {
    $(this).removeAttr('title');
  });

  updateSummary();

  $('#js-fundGrant').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      $('#token_symbol').val($('#js-token option:selected').text());

      let realPeriodSeconds = 0;

      if (data.frequency) {

        // translate timeAmount&timeType to requiredPeriodSeconds
        let periodSeconds = data.frequency;

        if (data.frequency_unit == 'days') {
          periodSeconds *= 86400;
        } else if (data.frequency_unit == 'hours') {
          periodSeconds *= 3600;
        } else if (data.frequency_unit == 'minutes') {
          periodSeconds *= 60;
        } else if (data.frequency_unit == 'months') {
          periodSeconds *= 2592000;
        }
        if (periodSeconds) {
          realPeriodSeconds = periodSeconds;
        }
      }

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);
      let deployedToken;
      let selected_token;

      if (data.token_address != '0x0000000000000000000000000000000000000000') {
        selected_token = data.token_address;
        deployedToken = new web3.eth.Contract(compiledToken.abi, data.token_address);
      } else {
        selected_token = data.denomination;
        deployedToken = new web3.eth.Contract(compiledToken.abi, data.denomination);
      }

      deployedToken.methods.decimals().call(function(err, decimals) {

        let realGasPrice = $('#gasPrice').val() * Math.pow(10, 9);

        $('#gas_price').val(realGasPrice);

        let realApproval = Number(((data.approve * 10 ** decimals) + realGasPrice) * data.amount_per_period);

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);

        web3.eth.getAccounts(function(err, accounts) {

          $('#contributor_address').val(accounts[0]);

          deployedToken.methods.approve(
            data.contract_address,
            web3.utils.toTwosComplement(realApproval)
          ).send({
            from: accounts[0],
            gasPrice: realGasPrice
          }).on('error', function(error) {
            console.log('1', error);
            alert('Your approval transaction failed. Please try again.');
          }).on('transactionHash', function(transactionHash) {
            $('#sub_new_approve_tx_id').val(transactionHash);
            document.issueURL = window.location.origin + $('#grant-link').val();
            enableWaitState('#grants_form');
            // Should add approval transactions to transaction history
            deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

              nonce = parseInt(nonce) + 1;

              const parts = [
                web3.utils.toChecksumAddress(accounts[0]), // subscriber address
                web3.utils.toChecksumAddress(data.admin_address), // admin_address
                web3.utils.toChecksumAddress(selected_token), // token denomination / address
                web3.utils.toTwosComplement(realTokenAmount), // data.amount_per_period
                web3.utils.toTwosComplement(realPeriodSeconds), // data.period_seconds
                web3.utils.toTwosComplement(realGasPrice), // data.gas_price
                web3.utils.toTwosComplement(nonce) // nonce
              ];

              deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash) {
                $('#subscription_hash').val(subscriptionHash);
                web3.eth.personal.sign('' + subscriptionHash, accounts[0], function(err, signature) {
                  $('#signature').val(signature);
                });
              });
            });
          }).on('confirmation', function(confirmationNumber, receipt) {
            $('#real_period_seconds').val(realPeriodSeconds);

            $.each($(form).serializeArray(), function() {
              data[this.name] = this.value;
            });

            form.submit();
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

      $("#js-token option[value='0x0000000000000000000000000000000000000000']").remove();
    });
    $('#js-token').select2();
  });
});

const updateSummary = (element) => {

  $('#summary-period').html($('input#frequency_count').val());
  $('#summary-amount').html($('input#amount').val() ? $('input#amount').val() : 0);
  $('#summary-frequency').html($('input#period').val() ? $('input#period').val() : 0);
  $('#summary-frequency-unit').html($('#frequency_unit').val());

  $('#js-token').on('select2:select', event => {
    $('#summary-token').html(event.params.data.text);
  });

  $('#frequency_unit').on('select2:select', event => {
    $('#summary-frequency-unit').html(event.params.data.text);
  });

  $('input#frequency_count').on('input', () => {
    $('#summary-period').html($('input#frequency_count').val());
  });

  $('input#amount').on('input', () => {
    $('#summary-amount').html($('input#amount').val());
  });

  $('input#period').on('input', () => {
    $('#summary-frequency').html($('input#period').val());
  });
};
