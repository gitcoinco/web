var estimate = function(amount, conv_rate) {
  var estimateAmount = amount * conv_rate;

  if (estimateAmount) {
    estimateAmount = Math.round(estimateAmount * 100) / 100;
    if (estimateAmount > 1000000) {
      estimateAmount = Math.round(estimateAmount / 100000) / 10 + 'm';
    } else if (estimateAmount > 1000) {
      estimateAmount = Math.round(estimateAmount / 100) / 10 + 'k';
    }
    return {'text': gettext('Approx: ') + estimateAmount + ' USD', 'value': estimateAmount};
  }
  return {'text': gettext('Approx: Unknown amount'), 'value': 0};
};

var usdToAmountEstimate = function(usd_amount, conv_rate) {
  var estimateAmount = usd_amount / conv_rate;

  if (estimateAmount) {
    estimateAmount = Math.round(estimateAmount * 1000) / 1000;
    if (estimateAmount > 1000000) {
      estimateAmount = Math.round(estimateAmount / 100000) / 10 + 'm';
    } else if (estimateAmount > 1000) {
      estimateAmount = Math.round(estimateAmount / 100) / 10 + 'k';
    }
    return estimateAmount;
  }
  return 0;
};

const get_rates_estimate = function(usd_amount) {
  let hours = $('#hours').val();

  if (!usd_amount || !hours || hours == 0) {
    return '';
  }

  let rates_addon = [];
  const rate = usd_amount / hours;
  const round_rate = rate.toFixed(0);
  const round_decimals = hours < 1 ? 2 : 1;

  hours = Math.round(hours, round_decimals);
  let success_prob = 100 * ((0.002 * rate) + 0.65);

  if (success_prob >= 100) {
    success_prob = 99;
  }

  if (hours) {
    rates_addon.push(`${hours} hrs at $${round_rate}/hr leads to <b>${success_prob.toFixed(0)}% success rate</b>. `);
  } else {
    rates_addon.push(`${hours} hrs at $&infin;/hr leads to <b>${success_prob.toFixed(0)}% success rate</b>. `);
  }
  rates_addon = rates_addon.join(', ');

  const help_addon = 'Read our <a href="https://medium.com/gitcoin/tutorial-how-to-price-work-on-gitcoin-49bafcdd201e" target="_blank" class="underline" rel="noopener noreferrer">pricing guide</a>.';

  return (rates_addon + help_addon);
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
    var return_text = usd_estimate['text'] + '<br>' + rate_estimate;
    var estimate_obj = {
      'full_text': return_text,
      'rate_text': rate_estimate,
      'value': usd_estimate['value'],
      'value_unrounded': Math.round(amount * conv_rate, 2)
    };

    return callback(estimate_obj);
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
    var return_text = usd_estimate['text'] + '<br>' + rate_estimate;
    var estimate_obj = {
      'full_text': return_text,
      'rate_text': rate_estimate,
      'value': usd_estimate['value'],
      'value_unrounded': Math.round(amount * conv_rate, 2)
    };

    return callback(estimate_obj);
  }).fail(function() {
    return callback(new Error(gettext('Approx: Unknown amount')));
  });
};

var getAmountEstimate = function(usd_amount, denomination, callback) {
  var conv_rate;
  var eth_usd;
  var eth_amount;
  var amount = 1;

  try {
    usd_amount = parseFloat(usd_amount);
  } catch (e) {
    return gettext('Incorrect amount');
  }
  if (document.conversion_rates && document.conversion_rates[denomination]) {
    conv_rate = document.conversion_rates[denomination];
    var amount_estimate = usdToAmountEstimate(usd_amount, conv_rate);

    rate_estimate = get_rates_estimate(amount_estimate * conv_rate);
    var estimate_obj = {
      'rate_text': rate_estimate,
      'value': amount_estimate
    };

    return callback(estimate_obj);
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
    var amount_estimate = usdToAmountEstimate(usd_amount, conv_rate);

    rate_estimate = get_rates_estimate(amount_estimate * conv_rate);
    var estimate_obj = {
      'rate_text': rate_estimate,
      'value': amount_estimate
    };

    return callback(estimate_obj);
  }).fail(function() {
    return callback(new Error(gettext('Approx: Unknown amount')));
  });
};
