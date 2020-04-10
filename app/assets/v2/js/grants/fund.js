/* eslint-disable no-console */
let deployedToken;
let deployedSubscription;
let tokenAddress;
let redirectURL;
let realPeriodSeconds = 0;
let selected_token;
let splitterAddress;
let gitcoinDonationAddress;

document.suppress_faucet_solicitation = 1;

var set_form_disabled = function(is_disabled) {
  if (is_disabled) {
    $('body').append('<div id=intercept_overlay>&nbsp;</div>');
  } else {
    $('#intercept_overlay').remove();
  }
};


$(document).ready(function() {


  // _alert({ message: gettext('Note: Brave users seem to have issues while contributing to Grants while using both Brave Wallet and MetaMask. We recommend disabling one. For more info, see this <a target="_blank" href="https://github.com/brave/brave-browser/issues/6053">issue</a>') }, 'warning');

  // set defaults
  var set_defaults = function() {
    var lookups = {
      'frequency_unit': '#frequency_unit',
      'token_address': 'select[name=denomination]',
      'recurring_or_not': '#recurring_or_not',
      'real_period_seconds': '#real_period_seconds',
      'amount_per_period': 'input#amount',
      'comment': 'textarea[name=comment]',
      'num_periods': 'input[name=num_periods]',
      'gitcoin-grant-input-amount': '#gitcoin-grant-input-amount'

    };

    for (key in lookups) {
      if (key) {
        const selector = lookups[key];
        const ls = localStorage.getItem('grants' + key);

        if (ls) {
          $(selector).val(ls);
          $(selector + ' option:eq("' + ls + '")').prop('selected', true);
        }
      }
    }
  };


  predictPhantomCLRMatch();
  predictCLRMatch();

  $('#amount').on('input', () => {
    predictCLRMatch();
  });

  gitcoinDonationAddress = $('#gitcoin_donation_address').val();
  splitterAddress = $('#splitter_contract_address').val();

  updateSummary();

  $('#grants_form .nav-item').click(function(e) {
    $('.nav-item a').removeClass('active');
    $(this).find('a').addClass('active');
    var targetid = $(this).find('a').data('target');
    var target = $('#' + targetid);

    $('.tab_target').addClass('hidden');
    target.removeClass('hidden');

    e.preventDefault();
  });

  $('#adjust').click(function(e) {
    $(this).remove();
    $('.unhide_if_expanded').removeClass('hidden');
    e.preventDefault();
  });

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

  $('input[name=match_direction]').change(function(e) {
    let direction = $(this).val();

    if (direction == '+') {
      $('.est_direction').text('increase').css('background-color', 'yellow');
      setTimeout(function() {
        $('.est_direction').css('background-color', 'white');
      }, 500);
      $('.hide_wallet_address_container').removeClass('hidden');
    } else {
      $('.est_direction').text('decrease').css('background-color', 'yellow');
      setTimeout(function() {
        $('.est_direction').css('background-color', 'white');
      }, 500);
      $('.hide_wallet_address_container').addClass('hidden');
    }
  });
  
  $('#js-token').change(function(e) {
    const val = $(this).val();
    const is_eth = val == '0x0000000000000000000000000000000000000000';

    if (val == '0xdac17f958d2ee523a2206206994597c13d831ec7') {
      _alert('WARNING: USDT is not well supported, it is recommended to use $USDC or $DAI instead. <a target=new href=https://twitter.com/owocki/status/1247546241862348801>More info here</a>', 'error', 2000);
    }

    if (is_eth && $('#recurring_or_not').val() == 'recurring') {
      _alert('Sorry but this token is not supported for recurring donations', 'error', 1000);
    }
    if (is_eth) {
      $('option[value=recurring]').attr('disabled', 'disabled');
      $('.contribution_type select').val('once').trigger('change');
    } else {
      $('option[value=recurring]').attr('disabled', null);
    }
  });


  $('.contribution_type select').change(function(e) {
    if ($('.contribution_type select').val() == 'once') {
      $('.frequency').addClass('hidden');
      $('.num_recurring').addClass('hidden');
      $('.hide_if_onetime').addClass('hidden');
      $('.hide_if_recurring').removeClass('hidden');
      $('#period').val(4);
      updateSummary();
      $('#amount_label').text('Amount');
      $('#negative').prop('disabled', '');
      $('label[for=negative]').css('color', 'black');
      $('#period').val(1);
    } else {
      $('.frequency').removeClass('hidden');
      $('.num_recurring').removeClass('hidden');
      $('#amount_label').text('Amount Per Period');
      $('.hide_if_onetime').removeClass('hidden');
      $('.hide_if_recurring').addClass('hidden');
      $('#positive').click();
      $('#negative').prop('disabled', 'disabled');
      $('label[for=negative]').css('color', 'grey');
    }
  });
  $('.contribution_type select').trigger('change');

  $('#js-fundGrant').submit(function(e) {
    e.preventDefault();
    var data = {};
    var form = $(this).serializeArray();

    $.each(form, function() {
      data[this.name] = this.value;
    });

    for (key in data) {
      if (key) {
        const val = data[key];
        var ls_key = 'grants' + key;

        localStorage.setItem(ls_key, val);
      }
    }
    localStorage.setItem('grantsrecurring_or_not', $('#recurring_or_not').val());
    localStorage.setItem('grantstoken_address', $('#js-token').val());
    localStorage.setItem('grantsgitcoin-grant-input-amount', $('#gitcoin-grant-input-amount').val());

    data.is_postive_vote = (data.match_direction == '-') ? 0 : 1;
  
    if (data.frequency_unit) {

      // translate timeAmount&timeType to requiredPeriodSeconds
      let periodSeconds = 1;

      if (data.frequency_unit == 'days') {
        periodSeconds *= 86400;
      } else if (data.frequency_unit == 'hours') {
        periodSeconds *= 3600;
      } else if (data.frequency_unit == 'minutes') {
        periodSeconds *= 60;
      } else if (data.frequency_unit == 'months') {
        periodSeconds *= 2592000;
      } else if (data.frequency_unit == 'rounds') {
        periodSeconds *= 2592001;
      }
      if (periodSeconds) {
        realPeriodSeconds = periodSeconds;
      }
    }

    if (data.contract_version == 0) {
      deployedSubscription = new web3.eth.Contract(compiledSubscription0.abi, data.contract_address);
    } else if (data.contract_version == 1) {
      deployedSubscription = new web3.eth.Contract(compiledSubscription1.abi, data.contract_address);
    }

    if (data.token_address != '0x0000000000000000000000000000000000000000') {
      selected_token = data.token_address;
      deployedToken = new web3.eth.Contract(compiledToken.abi, data.token_address);
    } else {
      selected_token = data.denomination;
      deployedToken = new web3.eth.Contract(compiledToken.abi, data.denomination);
      $('#token_symbol').val($('#js-token option:selected').text());
      $('#token_address').val(selected_token);
      data.token_address = selected_token;
    }

    if (!selected_token) {
      _alert('Please select a token', 'error');
      return;
    }

    // eth payments
    const is_eth = $('#js-token').val() == '0x0000000000000000000000000000000000000000';

    if (is_eth && $('#recurring_or_not').val() == 'recurring') {
      _alert('Sorry but ETH is not supported for recurring donations', 'error', 1000);
      return;
    }

    if (is_eth) {
      const percent = $('#gitcoin-grant-input-amount').val();
      const to_addr_amount = parseInt((100 - percent) * 0.01 * data.amount_per_period * 10 ** 18);
      const gitcoin_amount = parseInt((percent) * 0.01 * data.amount_per_period * 10 ** 18);

      web3.eth.getAccounts(function(err, accounts) {
        indicateMetamaskPopup();
        var to_address = data.match_direction == '+' ? data.admin_address : gitcoinDonationAddress;

        set_form_disabled(true);
        web3.eth.sendTransaction({
          from: accounts[0],
          to: to_address,
          value: to_addr_amount,
          gasPrice: parseInt(web3.utils.toHex($('#gasPrice').val() * Math.pow(10, 9)))
        }, function(err, txid) {
          indicateMetamaskPopup(1);
          if (err) {
            console.log(err);
            _alert('There was an error', 'error');
            set_form_disabled(false);
            return;
          }
          $('#gas_price').val(1);
          $('#sub_new_approve_tx_id').val(txid);

          var data = {};

          $.each($('#js-fundGrant').serializeArray(), function() {
            data[this.name] = this.value;
          });
          saveSubscription(data, true);
          var success_callback = function(err, new_txid) {
            indicateMetamaskPopup(1);
            if (err) {
              console.log(err);
              _alert('There was an error', 'error');
              set_form_disabled(false);
              return;
            }
            data = {
              'subscription_hash': 'onetime',
              'signature': 'onetime',
              'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
              'sub_new_approve_tx_id': txid
            };
            saveSplitTx(data, new_txid, true);

            waitforData(() => {
              document.suppress_loading_leave_code = true;
              window.location = window.location.href.replace('/fund', '');
            });

            const linkURL = get_etherscan_url(new_txid);

            document.issueURL = linkURL;

            $('#transaction_url').attr('href', linkURL);
            enableWaitState('#grants_form');
            set_form_disabled(false);
            $('#tweetModal').css('display', 'block');

          };

          if (!gitcoin_amount) {
            success_callback(null, txid);
          } else {
            indicateMetamaskPopup();
            web3.eth.sendTransaction({
              from: accounts[0],
              to: gitcoinDonationAddress,
              value: gitcoin_amount,
              gasPrice: parseInt(web3.utils.toHex($('#gasPrice').val() * Math.pow(10, 9)))
            }, success_callback);
          }
        });
      });
      return;
    }

    // erc20
    tokenAddress = data.token_address;

    deployedToken.methods.decimals().call(function(err, decimals) {
      if (err) {
        console.log(err);
        _alert('The token you selected is not a valid ERC20 token', 'error');
        return;
      }

      let realTokenAmount = Number(data.amount_per_period * Math.pow(10, decimals));
      let realApproval;

      const approve_buffer = 100000;
      if (data.contract_version == 1 || data.num_periods == 1) {

        realApproval = Number(((grant_amount + gitcoin_grant_amount) * data.num_periods * Math.pow(10, decimals)) + approve_buffer);
      } else if (data.contract_version == 0) {
        console.log('grant amount: ' + grant_amount);
        console.log('gitcoin grant amount: ' + gitcoin_grant_amount);
        // don't need to approve for gitcoin_grant_amount since we will directly transfer it
        realApproval = Number(((grant_amount * data.num_periods)) * Math.pow(10, decimals) + approve_buffer);
      }

      let realGasPrice = Number(gitcoin_grant_amount * Math.pow(10, decimals)); // optional grants fee

      if (contractVersion == 0) {
        realGasPrice = 1;
      }

      $('#gas_price').val(realGasPrice);

      let approvalSTR = realApproval.toLocaleString('fullwide', { useGrouping: false });

      web3.eth.getAccounts(function(err, accounts) {

        $('#contributor_address').val(accounts[0]);

        var approvalAddress;

        if (data.num_periods == 1) {
          approvalAddress = splitterAddress;
        } else {
          approvalAddress = data.contract_address;
        }

        // ERC20
        deployedToken.methods.balanceOf(
          accounts[0]
        ).call().then(function(result) {
          if (result < realTokenAmount) {
            _alert({ message: gettext('You do not have enough tokens to make this transaction.')}, 'error');
          } else {
            set_form_disabled(true);
            indicateMetamaskPopup();
            deployedToken.methods.approve(
              approvalAddress,
              web3.utils.toTwosComplement(approvalSTR)
            ).send({
              from: accounts[0],
              gasPrice: web3.utils.toHex(parseInt($('#gasPrice').val() * Math.pow(10, 9))),
              gas: web3.utils.toHex(gas_amount(document.location.href)),
              gasLimit: web3.utils.toHex(gas_amount(document.location.href))
            }).on('error', function(error) {
              indicateMetamaskPopup(true);
              set_form_disabled(false);
              console.log('1', error);
              _alert({ message: gettext('Your approval transaction failed. Please try again.')}, 'error');
            }).on('transactionHash', function(transactionHash) {
              indicateMetamaskPopup(true);
              $('#sub_new_approve_tx_id').val(transactionHash);
              if (data.num_periods == 1) {
                // call splitter after approval
                var to_address = data.match_direction == '+' ? data.admin_address : gitcoinDonationAddress;

                var first = Number(grant_amount * Math.pow(10, decimals)).toLocaleString('fullwide', {useGrouping: false});
                var second = Number(gitcoin_grant_amount * Math.pow(10, decimals)).toLocaleString('fullwide', {useGrouping: false});

                splitPayment(accounts[0], to_address, gitcoinDonationAddress, first, second);
              } else {
                if (data.contract_version == 0 && gitcoin_grant_amount > 0) {
                  donationPayment(deployedToken, accounts[0], Number(gitcoin_grant_amount * Math.pow(10, decimals)).toLocaleString('fullwide', {useGrouping: false}));
                }
                subscribeToGrant(transactionHash);
              }
            }).on('confirmation', function(confirmationNumber, receipt) {
              waitforData(() => {
                document.suppress_loading_leave_code = true;
                window.location = redirectURL;
              }); // waitforData
            }); // approve on confirmation
          } // if (result < realTokenAmount)
        }); // check token balance
      }); // getAccounts
    }); // decimals
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
      $("#js-token option[value='0x0000000000000000000000000000000000000001']").remove(); // ETC
      // $("#js-token option[value='0x0000000000000000000000000000000000000000']").remove(); // ETH
    });
    set_defaults();
    $('.js-select2').each(function() {
      $(this).select2();
    });
    $('#js-token').select2();
    $('#js-token').trigger('change');
    $('.contribution_type select').trigger('change');
    $('.select2-selection__rendered').hover(function() {
      $(this).removeAttr('title');
    });
    updateSummary();
  }); // waitforWeb3
}); // document ready

const donationPayment = (token, account, donationAmountString) => {
  token.methods.transfer(
    gitcoinDonationAddress,
    web3.utils.toTwosComplement(donationAmountString)
  ).send({
    from: account
  }).on('error', function(error) {
    console.log('One time old contract donation error:', error);
    _alert({ message: gettext('Your Gitcoin donation transaction failed. Please try again.')}, 'error');
  }).on('transactionHash', function(transactionHash) {
    console.log('One time old contract donation success: ' + transactionHash);
  });
};

const subscribeToGrant = (transactionHash) => {
  web3.eth.getAccounts(function(err, accounts) {
    deployedToken.methods.decimals().call(function(err, decimals) {
      const linkURL = get_etherscan_url(transactionHash);
      let data = {
        'contributor_address': $('#contributor_address').val(),
        'amount_per_period': grant_amount,
        'real_period_seconds': realPeriodSeconds,
        'frequency': $('#frequency_count').val(),
        'frequency_unit': $('#frequency_unit').val(),
        'token_address': selected_token,
        'token_symbol': $('#token_symbol').val(),
        'gas_price': $('#gas_price').val(),
        'sub_new_approve_tx_id': transactionHash,
        'num_tx_approved': $('#period').val(),
        'network': $('#network').val(),
        'match_direction': $('input[name=match_direction]:checked').val(),
        'is_postive_vote': ($('input[name=match_direction]:checked').val() == '-') ? 0 : 1,
        'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val()
      };

      $.ajax({
        type: 'post',
        url: '',
        data: data,
        success: () => {
          console.log('successfully saved subscription');
        },
        error: () => {
          _alert({ message: gettext('Your subscription failed to save. Please try again.') }, 'error');
        }
      });

      document.issueURL = linkURL;
      $('#transaction_url').attr('href', linkURL);
      enableWaitState('#grants_form');

      deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

        nonce = parseInt(nonce) + 1;

        const parts = [
          web3.utils.toChecksumAddress(accounts[0]), // subscriber address
          web3.utils.toChecksumAddress($('#admin_address').val()), // admin_address
          web3.utils.toChecksumAddress(selected_token), // token denomination / address
          web3.utils.toTwosComplement(Number(grant_amount * Math.pow(10, decimals)).toLocaleString('fullwide', {useGrouping: false})),
          web3.utils.toTwosComplement(realPeriodSeconds),
          web3.utils.toTwosComplement(data.gas_price),
          web3.utils.toTwosComplement(nonce)
        ];

        processSubscriptionHash(parts);
      });
    });
  });
};

const signSubscriptionHash = (subscriptionHash) => {
  web3.eth.getAccounts(function(err, accounts) {

    indicateMetamaskPopup();
    web3.eth.personal.sign('' + subscriptionHash, accounts[0], function(err, signature) {
      indicateMetamaskPopup(true);
      set_form_disabled(false);
      $('#tweetModal').css('display', 'block');

      if (signature) {
        $('#signature').val(signature);

        let data = {
          'subscription_hash': subscriptionHash,
          'signature': signature,
          'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
          'sub_new_approve_tx_id': $('#sub_new_approve_tx_id').val()
        };

        saveSubscription(data, false);
      }
    });
  });
};

const processSubscriptionHash = (parts) => {
  deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash) {
    $('#subscription_hash').val(subscriptionHash);
    signSubscriptionHash(subscriptionHash);
  });
};

const saveSubscription = (data, isOneTimePayment) => {
  if (isOneTimePayment) {
    data['real_period_seconds'] = 0;
    data['csrfmiddlewaretoken'] = $("#js-fundGrant input[name='csrfmiddlewaretoken']").val();
  }
  $.ajax({
    type: 'post',
    url: '',
    data: data,
    success: json => {
      console.log('successfully saved subscription');
      if (json.url != undefined) {
        redirectURL = json.url;
        $('#wait').val('false');
      }
    },
    error: (error) => {
      console.log(error);
      _alert({ message: gettext('Your subscription failed to save. Please try again.') }, 'error');
      redirectURL = window.location;
    }
  });
};

const saveSplitTx = (data, splitTxID, confirmed) => {
  if (splitTxID) {
    data['split_tx_id'] = splitTxID;
  }

  if (confirmed) {
    data['split_tx_confirmed'] = true;
  }

  $.ajax({
    type: 'post',
    url: '',
    data: data,
    success: json => {
      console.log('successfully saved subscription');
      if (json.url != undefined) {
        redirectURL = json.url;
        $('#wait').val('false');
      }
    },
    error: (error) => {
      console.log(error);
      _alert({ message: gettext('Your subscription failed to save. Please try again.') }, 'error');
      redirectURL = window.location;
    }
  });
};

const splitPayment = (account, toFirst, toSecond, valueFirst, valueSecond) => {
  var data = {};
  var form = $('#js-fundGrant');

  $.each($(form).serializeArray(), function() {
    data[this.name] = this.value;
  });

  saveSubscription(data, true);

  let deployedSplitter = new web3.eth.Contract(compiledSplitter.abiDefinition, splitterAddress);

  let token_address = $('#js-token').length ? $('#js-token').val() : $('#sub_token_address').val();

  indicateMetamaskPopup();
  deployedSplitter.methods.splitTransfer(toFirst, toSecond, valueFirst, valueSecond, tokenAddress).send({
    from: account,
    gas: web3.utils.toHex(100000),
    gasPrice: parseInt(web3.utils.toHex($('#gasPrice').val() * Math.pow(10, 9)))
  }).on('error', function(error) {
    console.log('1', error);
    indicateMetamaskPopup(1);
    set_form_disabled(false);
    _alert({ message: gettext('Your payment transaction failed. Please try again.')}, 'error');
  }).on('transactionHash', function(transactionHash) {
    indicateMetamaskPopup(1);
    set_form_disabled(false);
    $('#tweetModal').css('display', 'block');
    data = {
      'subscription_hash': 'onetime',
      'signature': 'onetime',
      'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
      'sub_new_approve_tx_id': $('#sub_new_approve_tx_id').val()
    };
    saveSplitTx(data, transactionHash, false);

    waitforData(() => {
      document.suppress_loading_leave_code = true;
      window.location = redirectURL;
    });

    const linkURL = get_etherscan_url(transactionHash);

    document.issueURL = linkURL;

    $('#transaction_url').attr('href', linkURL);
    enableWaitState('#grants_form');
    set_form_disabled(false);
    $('#tweetModal').css('display', 'block');
  }).on('confirmation', function(confirmationNumber, receipt) {
    data = {
      'subscription_hash': 'onetime',
      'signature': 'onetime',
      'csrfmiddlewaretoken': $("#js-fundGrant input[name='csrfmiddlewaretoken']").val(),
      'sub_new_approve_tx_id': $('#sub_new_approve_tx_id').val()
    };
    console.log('confirmed!');
    saveSubscription(data, true);
    saveSplitTx(data, false, true);
  });
};

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
  contract_version = $('#contract_version').val();

  $('.summary-period').html($('#period').val());
  $('.summary-period-gitcoin').html($('#period').val());
  $('.summary-frequency-unit').html($('#frequency_unit').val());
  $('.summary-frequency-unit-gitcoin').html($('#frequency_unit').val());

  if (contract_version == 0) {
    $('.summary-period-gitcoin').html('');
    $('.summary-frequency-unit-gitcoin').html('');
    $('.summary-rollup-gitcoin').hide();
  }

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
  contract_version = $('#contract_version').val();
  num_periods = $('#period').val();

  const percent = $('#gitcoin-grant-input-amount').val();
  const total_amount = $('input#amount').val() ? $('input#amount').val() : 0;

  if (total_amount != 0) {
    if (!percent) {
      $('#summary-gitcoin-grant').hide();
      grant_amount = Number($('input#amount').val());
    } else {
      $('#summary-gitcoin-grant').show();
      if (contract_version == 0) {
        gitcoin_grant_amount = parseFloat(Number(num_periods * percent / 100 * Number($('input#amount').val())).toFixed(4));
        grant_amount = parseFloat((Number($('input#amount').val())).toFixed(4));
      } else {
        gitcoin_grant_amount = parseFloat(Number(percent / 100 * Number($('input#amount').val())).toFixed(4));
        grant_amount = parseFloat((Number($('input#amount').val()) - gitcoin_grant_amount).toFixed(4));
      }
    }
  }

  $('.gitcoin-grant-percent').html(percent);
  $('.summary-gitcoin-amount').html(gitcoin_grant_amount.toFixed(3));
  $('#summary-amount').html(grant_amount);
};

const lerp = (x_lower, x_upper, y_lower, y_upper, x) => {
  return y_lower + (((y_upper - y_lower) * (x - x_lower)) / (x_upper - x_lower));
};

const predictPhantomCLRMatch = () => {

  let amount = phantom_value;

  if (typeof clr_prediction_curve_per_grant == 'undefined') {
    return;
  }
  for (var grant_id in clr_prediction_curve_per_grant) {
    if (grant_id) {
      var curve_per_grant = clr_prediction_curve_per_grant[grant_id].map(function(value, index) {
        return value[1];
      });

      if (0 <= amount && amount <= 1) {
        x_lower = 0;
        x_upper = 1;
        y_lower = curve_per_grant[0];
        y_upper = curve_per_grant[1];
      } else if (1 < amount && amount <= 10) {
        x_lower = 1;
        x_upper = 10;
        y_lower = curve_per_grant[1];
        y_upper = curve_per_grant[2];
      }
      let predicted_clr = lerp(x_lower, x_upper, y_lower, y_upper, amount);

      $('.phantom_clr_increase' + grant_id).html((predicted_clr - curve_per_grant[0]).toFixed(2));
    }
  }
};

const predictCLRMatch = () => {

  let amount = Number.parseFloat($('#amount').val());

  if (amount > 10000) {
    amount = 10000;
  }

  let predicted_clr = 0;

  const contributions_axis = [ 0, 1, 10, 100, 1000, 10000 ];

  let index = 0;

  if (isNaN(amount)) {
    predicted_clr = clr_prediction_curve[index];
  } else if (contributions_axis.indexOf(amount) >= 0) {
    index = contributions_axis.indexOf(amount);
    predicted_clr = clr_prediction_curve[index];
  } else {
    let x_lower = 0;
    let x_upper = 0;
    let y_lower = 0;
    let y_upper = 0;

    if (0 < amount && amount < 1) {
      x_lower = 0;
      x_upper = 1;
      y_lower = clr_prediction_curve[0];
      y_upper = clr_prediction_curve[1];
    } else if (1 < amount && amount < 10) {
      x_lower = 1;
      x_upper = 10;
      y_lower = clr_prediction_curve[1];
      y_upper = clr_prediction_curve[2];
    } else if (10 < amount && amount < 100) {
      x_lower = 10;
      x_upper = 100;
      y_lower = clr_prediction_curve[2];
      y_upper = clr_prediction_curve[3];
    } else if (100 < amount && amount < 1000) {
      x_lower = 100;
      x_upper = 1000;
      y_lower = clr_prediction_curve[3];
      y_upper = clr_prediction_curve[4];
    } else {
      x_lower = 1000;
      x_upper = 10000;
      y_lower = clr_prediction_curve[4];
      y_upper = clr_prediction_curve[5];
    }

    predicted_clr = lerp(x_lower, x_upper, y_lower, y_upper, amount);
  }

  $('.clr_match_prediction').html(predicted_clr.toFixed(2));
  $('.clr_increase').html((predicted_clr - clr_prediction_curve[0]).toFixed(2));
};

const predictCLRLive = (amount) => {
  const grant_id = $('#grant_id').val();
  const url = `/grants/api/v1/${grant_id}/predict-clr?amount=${amount}`;

  fetchData (url, 'GET').then(response => {
    if (200 == response.status) {
      // SUCCESS
      console.log('clr match', response.clr_match);
    } else {
      // FAILURE
      console.error(`error: predictCLRLive - status ${response.status} - ${response.message}`);
    }
  });
};