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
        $('#sub_token_address').val(data.token_address);
      } else {
        selected_token = data.denomination;
        deployedToken = new web3.eth.Contract(compiledToken.abi, data.denomination);
        $('#token_symbol').val($('#js-token option:selected').text());
      }

      deployedToken.methods.decimals().call(function(err, decimals) {

        let realGasPrice = Math.ceil($('#gasPrice').val() * Math.pow(10, 9));

        $('#gas_price').val(realGasPrice);

        let realTokenAmount = Number(data.amount_per_period * Math.pow(10, decimals));
        let amountSTR = realTokenAmount.toLocaleString('fullwide', { useGrouping: false });

        let realApproval = Number((realTokenAmount + realGasPrice) * data.num_periods);
        let approvalSTR = realApproval.toLocaleString('fullwide', { useGrouping: false });

        web3.eth.getAccounts(function(err, accounts) {

          $('#contributor_address').val(accounts[0]);

          deployedToken.methods.approve(
            data.contract_address,
            web3.utils.toTwosComplement(approvalSTR)
          ).send({
            from: accounts[0],
            gasPrice: realGasPrice
          }).on('error', function(error) {
            console.log('1', error);
            _alert({ message: gettext('Your approval transaction failed. Please try again.')}, 'error');
          }).on('transactionHash', function(transactionHash) {
            $('#sub_new_approve_tx_id').val(transactionHash);
            const linkURL = etherscan_tx_url(transactionHash);

            document.issueURL = linkURL;
            $('#transaction_url').attr('href', linkURL);
            enableWaitState('#grants_form');
            // Should add approval transactions to transaction history
            deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

              nonce = parseInt(nonce) + 1;

              const parts = [
                web3.utils.toChecksumAddress(accounts[0]), // subscriber address
                web3.utils.toChecksumAddress(data.admin_address), // admin_address
                web3.utils.toChecksumAddress(selected_token), // token denomination / address
                web3.utils.toTwosComplement(amountSTR), // data.amount_per_period
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

            waitforData(function() {
              $.each($(form).serializeArray(), function() {
                data[this.name] = this.value;
              });
              document.suppress_loading_leave_code = true;
              form.submit();
            });
          });
        });
      });
    }
  });

  waitforWeb3(function() {
    if (document.web3network != $('#network').val()) {
      $('#js-fundGrant-button').prop('disabled', true);
      let network = $('#network').val();

      _alert({ message: gettext('This Grant is on the ' + network + ' network. Please, switch to ' + network + ' to contribute to this grant.') }, 'error');
    }

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

var waitforData = function(callback) {
  if ($('#signature').val() != '') {
    callback();
  } else {
    var wait_callback = function() {
      waitforData(callback);
    };

    setTimeout(wait_callback, 3000);
  }
};

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
