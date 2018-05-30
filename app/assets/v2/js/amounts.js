var estimate = function(amount, conv_rate) {
  var estimateAmount = amount * conv_rate;

  if (estimateAmount) {
    estimateAmount = Math.round(estimateAmount * 100) / 100;
    if (estimateAmount > 1000000) {
      estimateAmount = Math.round(estimateAmount / 100000) / 10 + 'm';
    } else if (estimateAmount > 1000) {
      estimateAmount = Math.round(estimateAmount / 100) / 10 + 'k';
    }
    return gettext('Approx: ') + estimateAmount + ' USD';
  }
  return gettext('Approx: Unknown amount');
};

var get_rates_estimate = function(usd_amount) {
  if (!usd_amount) {
    return '';
  }
  var rates_addon = [];
  var rates = [ 40, 80, 120 ];

  for (var i = 0; i < rates.length; i++) {
    var rate = rates[i];
    var hours = usd_amount / rate;
    var round_decimals = hours < 1 ? 2 : 1;

    hours = Math.round(hours, round_decimals);
    rates_addon.push('' + hours + ' hrs at $' + rate + '/hr');
  }
  rates_addon = rates_addon.join(', ');

  var help_addon = ' <a href="https://medium.com/gitcoin/tutorial-how-to-price-work-on-gitcoin-49bafcdd201e">[Read our pricing guide]</a>';
  var final_text = rates_addon + help_addon;

  return final_text;
};

var getUSDEstimate = function(amount, denomination, callback) {
  var conv_rate;
  var eth_usd;
  var eth_amount;

  try {
    amount = parseFloat(amount);
  } catch (e) {
    return gettext('Incorrect amount');
  }
  if (document.conversion_rates && document.conversion_rates[denomination]) {
    conv_rate = document.conversion_rates[denomination];
    var usd_estimate = estimate(amount, conv_rate);

    rate_estimate = get_rates_estimate(amount * conv_rate);
    var return_text = usd_estimate + '<br>' + rate_estimate;

    return callback(return_text);
  }
  var request_url = '/sync/get_amount?amount=' + amount + '&denomination=' + denomination;

  jQuery.get(request_url, function(result) {
    amount_usdt = result['usdt'];
    eth_amount = parseFloat(result['eth']);
    conv_rate = amount_usdt / amount;
    // store conv rate for later in cache
    if (typeof document.conversion_rates == 'undefined') {
      document.conversion_rates = {};
    }
    document.conversion_rates[denomination] = conv_rate;
    var usd_estimate = estimate(amount, conv_rate);

    rate_estimate = get_rates_estimate(amount * conv_rate);
    var return_text = usd_estimate + '<br>' + rate_estimate;

    return callback(return_text);
  }).fail(function() {
    return callback(new Error(gettext('Approx: Unknown amount')));
  });
};
