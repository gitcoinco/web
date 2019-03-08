/* eslint-disable no-console */
$(document).ready(function() {

  $('.js-select2').each(function() {
    $(this).select2();
  });

  $('.select2-selection__rendered').hover(function() {
    $(this).removeAttr('title');
  });

  updateSummary();

  $('#frequency_unit, #js-token').on('select2:select', event => {
    updateSummary();
  });

  $('input#frequency_count, input#amount, input#period').on('input', () => {
    updateSummary();
  });

  $('.contribution_type select').change(function() {
    if ($('.contribution_type select').val() == 'once') {
      $('.frequency').addClass('hidden');
      $('.num_recurring').addClass('hidden');
      $('.hide_if_onetime').addClass('hidden');
      $('.hide_if_recurring').removeClass('hidden');
      $('#period').val(1);
      updateSummary();
      $('#amount_label').text('Amount');
    } else {
      $('.frequency').removeClass('hidden');
      $('.num_recurring').removeClass('hidden');
      $('#amount_label').text('Amount Per Period');
      $('.hide_if_onetime').removeClass('hidden');
      $('.hide_if_recurring').addClass('hidden');
    }
  });

  $('#js-fundGrant').validate({
    rules: {
      num_periods: {
        required: true,
        min: 1
      }
    },
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
      } else {
        selected_token = data.denomination;
        deployedToken = new web3.eth.Contract(compiledToken.abi, data.denomination);
        $('#token_symbol').val($('#js-token option:selected').text());
      }
      if (!selected_token) {
        _alert('Please select a token', 'error');
        return;
      }

      deployedToken.methods.decimals().call(function(err, decimals) {
        if (err) {
          _alert('The token you selected is not a valid ERC20 token', 'error');
          return;
        }

        let realGasPrice = 0; // zero cost metatxs

        if (realPeriodSeconds < 2592000) {
          // charge gas for intervals less than a month
          realGasPrice = Math.ceil($('#gasPrice').val() * Math.pow(10, 9));
        }

        $('#gas_price').val(realGasPrice);

        let realTokenAmount = Number(data.amount_per_period * Math.pow(10, decimals));
        let amountSTR = realTokenAmount.toLocaleString('fullwide', { useGrouping: false });

        let realApproval = Number((realTokenAmount + realGasPrice) * data.num_periods);
        let approvalSTR = realApproval.toLocaleString('fullwide', { useGrouping: false });

        web3.eth.getAccounts(function(err, accounts) {

          $('#contributor_address').val(accounts[0]);

          let url;

          var tokenMethod = deployedToken.methods.approve;
          var arg1 = data.contract_address;

          // one time payments
          if (data.num_periods == 1) {
            arg1 = data.admin_address;
            tokenMethod = deployedToken.methods.transfer;
          }

          tokenMethod(
            arg1,
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
            let token_address = $('#js-token').length ? $('#js-token').val() : $('#sub_token_address').val();
            let data = {
              'contributor_address': $('#contributor_address').val(),
              'amount_per_period': $('#amount').val(),
              'real_period_seconds': realPeriodSeconds,
              'frequency': $('#frequency_count').val(),
              'frequency_unit': $('#frequency_unit').val(),
              'token_address': selected_token,
              'token_symbol': $('#token_symbol').val(),
              'gas_price': $('#gas_price').val(),
              'sub_new_approve_tx_id': transactionHash,
              'num_tx_approved': $('#period').val(),
              'network': $('#network').val(),
              'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val()
            };

            $.ajax({
              type: 'post',
              url: '',
              data: data,
              success: json => {
                console.log('successfully saved subscription');
              },
              error: () => {
                _alert({ message: gettext('Your subscription failed to save. Please try again.') }, 'error');
              }
            });

            document.issueURL = linkURL;
            $('#transaction_url').attr('href', linkURL);
            enableWaitState('#grants_form');
            // Should add approval transactions to transaction history
            deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

              nonce = parseInt(nonce) + 1;

              const parts = [
                web3.utils.toChecksumAddress(accounts[0]), // subscriber address
                web3.utils.toChecksumAddress($('#admin_address').val()), // admin_address
                web3.utils.toChecksumAddress(selected_token), // token denomination / address
                web3.utils.toTwosComplement(amountSTR), // data.amount_per_period
                web3.utils.toTwosComplement(realPeriodSeconds), // data.period_seconds
                web3.utils.toTwosComplement(realGasPrice), // data.gas_price
                web3.utils.toTwosComplement(nonce) // nonce
              ];

              deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash) {
                $('#subscription_hash').val(subscriptionHash);
                web3.eth.personal.sign('' + subscriptionHash, accounts[0], function(err, signature) {
                  if (signature) {
                    $('#signature').val(signature);

                    let data = {
                      'subscription_hash': subscriptionHash,
                      'signature': signature,
                      'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
                      'sub_new_approve_tx_id': $('#sub_new_approve_tx_id').val()
                    };

                    $.ajax({
                      type: 'post',
                      url: '',
                      data: data,
                      success: json => {
                        console.log('successfully saved subscriptionHash and signature');
                        url = json.url;
                        $('#wait').val('false');
                      },
                      error: () => {
                        _alert({ message: gettext('Your subscription failed to save. Please try again.') }, 'error');
                        url = window.location;
                      }
                    });
                  }
                });
              });
            });
          }).on('confirmation', function(confirmationNumber, receipt) {

            waitforData(() => {
              document.suppress_loading_leave_code = true;
              window.location = url;
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

const waitforData = (callback) => {
  if ($('#wait').val() === 'false') {
    callback();
  } else {
    var wait_callback = () => {
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
  if ($('#token_symbol').val() === 'Any Token') {
    $('#summary-token').html($('#js-token option:selected').text());
  }

};
