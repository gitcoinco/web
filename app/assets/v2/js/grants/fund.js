/* eslint-disable no-console */
let deployedToken;
let tokenAddress;
let redirectURL;

$(document).ready(function() {
  let gitcoinDonationAddress = "0x0000000000000000000000000000000000000000";

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

  $('#gitcoin-grant-input-amount').on('input', () => {
    $('.bot-heart').hide();
    updateSummary();

    if ($('#gitcoin-grant-input-amount').val() == 0) {
      $('#bot-heartbroken').show();
    } else if ($('#gitcoin-grant-input-amount').val() >= 20) {
      $('#bot-heart-20').show();
    } else if ($('#gitcoin-grant-input-amount').val() >= 15) {
      $('#bot-heart-15').show();
    } else if ($('#gitcoin-grant-input-amount').val() >= 10) {
      $('#bot-heart-10').show();
    } else if ($('#gitcoin-grant-input-amount').val() > 0) {
      $('#bot-heart-5').show();
    }
  });

  $('#gitcoin-grant-input-amount').on('focus', () => {
    $('#gitcoin-grant-input-amount').removeClass('inactive');
    $('#gitcoin-grant-section .badge').addClass('inactive');
  });

  $('#gitcoin-grant-section .badge').on('click', event => {

    $('#gitcoin-grant-section .badge').removeClass('inactive');
    $('#gitcoin-grant-input-amount').addClass('inactive');

    const percentage = Number(event.currentTarget.getAttribute('data-percent'));

    $('#gitcoin-grant-input-amount').val(percentage);
    $('.gitcoin-grant-percent').val(percentage);

    $('#gitcoin-grant-input-amount').trigger('input');

    $('#gitcoin-grant-section .badge').removeClass('badge-active');
    $('#gitcoin-grant-section .badge').addClass('badge-inactive');

    $(event.currentTarget).removeClass('badge-inactive');
    $(event.currentTarget).addClass('badge-active');
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
      if (data.contract_version == 0) {
        let deployedSubscription = new web3.eth.Contract(compiledSubscription0.abi, data.contract_address);
      } else if (data.contract_version == 1) {
        let deployedSubscription = new web3.eth.Contract(compiledSubscription1.abi, data.contract_address);
      }
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
      tokenAddress = data.token_address;

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

        let realApproval;
        if (data.contract_version == 0) {
          // version 0 of the contract has no fee
          realApproval = Number((grant_amount * data.num_periods * Math.pow(10, decimals)) + 1);
        } else if (data.contract_version == 1) {
          realApproval = Number(((grant_amount + gitcoin_grant_amount) * data.num_periods * Math.pow(10, decimals)) + 1);
        }
        let approvalSTR = realApproval.toLocaleString('fullwide', { useGrouping: false });

        web3.eth.getAccounts(function(err, accounts) {

          $('#contributor_address').val(accounts[0]);

          let url;

          deployedToken.methods.approve(
            data.contract_address,
            web3.utils.toTwosComplement(approvalSTR)
          ).send({
            from: accounts[0],
            // TODO: this is not the correct variable, this is for the metatx
            //gasPrice: realGasPrice
          }).on('error', function(error) {
            console.log('1', error);
            _alert({ message: gettext('Your approval transaction failed. Please try again.')}, 'error');
          }).on('transactionHash', function(transactionHash) {
            if (data.num_periods == 1) {
              //call splitter after approval
              splitPayment(accounts[0], data.admin_address, gitcoinDonationAddress, Number(grant_amount * Math.pow(10, decimals)).toLocaleString('fullwide', {useGrouping: false}), Number(gitcoin_grant_amount * Math.pow(10, decimals)).toLocaleString('fullwide', {useGrouping: false}));
            } else {
              subscribeToGrant(transactionHash);
            }
          }).on('confirmation', function(confirmationNumber, receipt) {
            waitforData(() => {
              document.suppress_loading_leave_code = true;
              window.location = redirectURL;
            }); // waitforData
          }); // approve
        }); // getAccounts
      }); // decimals
    } // submitHandler
  }); // validate

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
  }); // waitforWeb3
}); // document ready

const subscribeToGrant = (transactionHash, grant_version) => {
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
  $('#tweetModal').modal('show');
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

    processSubscriptionHash(parts);
  });
}

const signSubscriptionHash = (subscriptionHash) => {
  web3.eth.personal.sign('' + subscriptionHash, accounts[0], function(err, signature) {
    if (signature) {
      $('#signature').val(signature);

      let data = {
        'subscription_hash': subscriptionHash,
        'signature': signature,
        'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
        'sub_new_approve_tx_id': $('#sub_new_approve_tx_id').val()
      };

      saveSubscription(data);
    };
  });
}

const processSubscriptionHash = (parts) => {
  deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash) {
    $('#subscription_hash').val(subscriptionHash);
    signSubscriptionHash(subscriptionHash);
  });
}

const saveSubscription = (data) => {
  console.log(data);
  data['real_period_seconds'] = 0;
  $.ajax({
    type: 'post',
    url: '',
    data: data,
    success: json => {
      console.log(json);
      console.log('successfully saved subscriptionHash and signature');
      if (json.url != undefined) {
        redirectURL = json.url;
        $('#wait').val('false');
      }
    },
    error: (error) => {
      console.log(error);
      _alert({ message: gettext('Your subscription failed to save. Please try again.') }, 'error');
      url = window.location;
    }
  });
}

const splitPayment = (account, toFirst, toSecond, valueFirst, valueSecond) => {
  var data = {};
  var form = $('#js-fundGrant');
  $.each($(form).serializeArray(), function() {
    data[this.name] = this.value;
  });
  saveSubscription(data);
  let deployedSplitter = new web3.eth.Contract(compiledSplitter.abiDefinition, "0xe2fd6dfe7f371e884e782d46f043552421b3a9d9");

  console.log('deployed splitter is ' + deployedSplitter);

  deployedSplitter.methods.splitTransfer(toFirst, toSecond, valueFirst, valueSecond, tokenAddress).send({
    from: account
  }).on('error', function(error) {
    console.log('1', error);
    _alert({ message: gettext('Your payment transaction failed. Please try again.')}, 'error');
  }).on('transactionHash', function(transactionHash) {
    waitforData(() => {
      document.suppress_loading_leave_code = true;
      console.log('loading url: ' + redirectURL);
      window.location = redirectURL;
    });

    const linkURL = etherscan_tx_url(transactionHash);
    document.issueURL = linkURL;

    $('#transaction_url').attr('href', linkURL);
    enableWaitState('#grants_form');
    //$('#tweetModal').modal('show');
  }).on('confirmation', function(confirmationNumber, receipt) {
    data = {
      'subscription_hash': 'onetime',
      'signature': 'onetime',
      'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
      'sub_new_approve_tx_id': $('#sub_new_approve_tx_id').val()
    };
    console.log('confirmed!');
    saveSubscription(data);
  });
}

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

// Updates summary section
const updateSummary = (element) => {

  $('.summary-period').html($('input#frequency_count').val());
  $('.summary-frequency-unit').html($('#frequency_unit').val());
  $('.summary-frequency').html($('input#period').val() ? $('input#period').val() : 0);

  if ($('#token_symbol').val() === 'Any Token') {
    $('.summary-token').html($('#js-token option:selected').text());
  }

  splitGrantAmount();
};

let gitcoin_grant_amount = 0;
let grant_amount = 0;

// Splits the total amount between the grant & gitcoin grant in the summary section
const splitGrantAmount = () => {
  const percent = $('#gitcoin-grant-input-amount').val();
  const total_amount = $('input#amount').val() ? $('input#amount').val() : 0;


  if (total_amount != 0) {
    if (!percent || percent == 0) {
      $('#summary-gitcoin-grant').hide();
      grant_amount = Number($('input#amount').val());
    } else {
      $('#summary-gitcoin-grant').show();
      gitcoin_grant_amount = parseFloat(Number(percent / 100 * Number($('input#amount').val())).toFixed(4));
      grant_amount = parseFloat((Number($('input#amount').val()) - gitcoin_grant_amount).toFixed(4));
    }
  }

  $('.gitcoin-grant-percent').html(percent);
  $('.summary-gitcoin-amount').html(gitcoin_grant_amount);
  $('#summary-amount').html(grant_amount);
};
