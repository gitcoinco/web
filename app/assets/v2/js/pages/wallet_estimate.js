window.addEventListener('load', function() {
  try {
    if (web3 && web3.currentProvider.isTrust) {
      $('#trust_label').show();
    } else {
      $('#metamask_label').show();
    }
  } catch (ignore) {
    console.log('%c error: web3 not defined. ensure metamask is installed & unlocked', 'color: red');
  }
  setTimeout(prefill_recommended_prices, 1000);

  $(document).on('click', '#accordion-set-own-limit', function() {
    $('#metamask_context').toggle();
    $('#gas-section .recommended-prices').removeClass('active');
    if ($('#accordion-set-own-limit i').hasClass('fa-angle-down')) {
      $('#accordion-set-own-limit i').removeClass('fa-angle-down').addClass('fa-angle-up');
    } else {
      $('#accordion-set-own-limit i').removeClass('fa-angle-up').addClass('fa-angle-down');
    }
  });

  $(document).on('click', '#gas-section .recommended-prices', function() {
    var gasLimit = parseInt($('#gasLimit').val());
    var usdAmount = $(this).data('amount-usd');
    var ethAmount = Math.round(1000000 * usdAmount / document.eth_usd_conv_rate) / 1000000;
    var gasPrice = $(this).data('amount');

    $('#gas-section .recommended-prices').removeClass('active');
    $(this).addClass('active');
    $('#gas-usd').html('$' + usdAmount);
    $('#gas-eth').html(ethAmount + 'ETH');
    gasPrice = Math.round(gasPrice * 10) / 10.0;
    if (gasPrice < 0.1) {
      gasPrice = 0.1;
    }
    $('#gasPrice').val(gasPrice);
    update_metamask_conf_time_and_cost_estimate();
  });
});

function gasToUSD(gasPrice) {
  var gasLimit = parseInt($('#gasLimit').val());
  var ethAmount = Math.round(1000 * gasLimit * gasPrice / Math.pow(10, 9)) / 1000;
  var usdAmount = Math.round(10 * ethAmount * document.eth_usd_conv_rate) / 10;

  return usdAmount;
}

function get_recommended_prices() {
  var slow_price_index = Math.round(document.conf_time_spread.length / 9);
  var avg_price_index = Math.round(document.conf_time_spread.length / 3);
  var fast_price_index = Math.round(document.conf_time_spread.length / 9 * 5);

  var slow_price_range = [];

  for (var i = 0; i < document.conf_time_spread.length; i++) {
    if (gasPrice <= parseFloat(next_ele[0]) && gasPrice > parseFloat(this_ele[0])) {
      confTime = Math.round(10 * next_ele[1]) / 10;
    }
  }

  var recommendations = {
    'slow': {
      'amount': gasToUSD(document.conf_time_spread[slow_price_index][0]),
      'time': document.conf_time_spread[slow_price_index][1]
    },
    'avg': {
      'amount': gasToUSD(document.conf_time_spread[avg_price_index][0]),
      'time': document.conf_time_spread[avg_price_index][1]
    },
    'fast': {
      'amount': gasToUSD(document.conf_time_spread[fast_price_index][0]),
      'time': document.conf_time_spread[fast_price_index][1]
    }
  };

  return recommendations;
}

function prefill_recommended_prices() {
  var slow_data = get_updated_metamask_conf_time_and_cost(parseFloat($('#slow-recommended-gas').data('amount')));
  var avg_data = get_updated_metamask_conf_time_and_cost(parseFloat($('#average-recommended-gas').data('amount')));
  var fast_data = get_updated_metamask_conf_time_and_cost(parseFloat($('#fast-recommended-gas').data('amount')));

  if (fast_data['time'] == 'unknown') {
    $('#default-recommended-gas').show();
    $('#default-recommended-gas').html('The confirmation time is unknown. <br> However we recommend a gas price of $' + parseFloat(fast_data['usd']).toFixed(2));
    $('#default-recommended-gas').data('amount-usd', parseFloat(fast_data['usd']).toFixed(2));
    $('#gasPriceRecommended').val($('#average-recommended-gas').data('amount'));
    $('#slow-recommended-gas').hide();
    $('#average-recommended-gas').hide();
    $('#fast-recommended-gas').hide();
    let new_gas_price = Math.round($('#average-recommended-gas').data('amount') * 10) / 10;

    $('#gasPrice').val(new_gas_price);
    $('#gas-usd').html('$' + parseFloat(fast_data['usd']).toFixed(2));
    $('#gas-eth').html(avg_data['eth'] + 'ETH');
  } else if (slow_data['time'] < 20 && parseFloat($('#slow-recommended-gas').data('amount')) < 2) {
    $('#slow-recommended-gas').hide();
    $('#default-recommended-gas').hide();
    $('#average-recommended-gas').hide();
    $('#fast-recommended-gas').show();
    $('.gas-rates .message').html('Good news! The network is pretty fast right now').show();
    $('#fast-recommended-gas').html('Fast $' + parseFloat(fast_data['usd']).toFixed(2) + ' ~' + fast_data['time'] + ' minutes').addClass('active');
    $('#fast-recommended-gas').data('amount-usd', parseFloat(fast_data['usd']).toFixed(2));
    $('#fast-recommended-gas').parent().removeClass('justify-content-between').addClass('justify-content-around');
    let new_gas_price = Math.round($('#average-recommended-gas').data('amount') * 10) / 10;

    $('#gasPrice').val(new_gas_price);
    $('#gas-usd').html('$' + parseFloat(fast_data['usd']).toFixed(2));
    $('#gas-eth').html(fast_data['eth'] + 'ETH');
  } else {
    $('#fast-recommended-gas').parent().addClass('justify-content-between').removeClass('justify-content-around');
    let new_gas_price = Math.round($('#average-recommended-gas').data('amount') * 10) / 10;

    $('#gasPrice').val(new_gas_price);
    $('#gas-usd').html('$' + parseFloat(avg_data['usd']).toFixed(2));
    $('#gas-eth').html(avg_data['eth'] + 'ETH');
  }

  // Slow recommendation prefills
  $('#slow-recommended-gas').html('Slow $' + parseFloat(slow_data['usd']).toFixed(2) + ' ~' + slow_data['time'] + ' minutes');
  $('#slow-recommended-gas').data('amount-usd', parseFloat(slow_data['usd']).toFixed(2));

  // Avg recommendation prefills
  $('#average-recommended-gas').html('Average $' + parseFloat(avg_data['usd']).toFixed(2) + ' ~' + avg_data['time'] + ' minutes');
  $('#average-recommended-gas').data('amount-usd', parseFloat(avg_data['usd']).toFixed(2));

  // Fast recommendation prefills
  $('#fast-recommended-gas').html('Fast $' + parseFloat(fast_data['usd']).toFixed(2) + ' ~' + fast_data['time'] + ' minutes');
  $('#fast-recommended-gas').data('amount-usd', parseFloat(fast_data['usd']).toFixed(2));
}
