var estimate = function(amount, conv_rate) {
  var estimateAmount = amount * conv_rate;

  if (estimateAmount) {
    estimateAmount = Math.round(estimateAmount * 100) / 100;
    if (estimateAmount > 1000000) {
      estimateAmount = Math.round(estimateAmount / 100000) / 10 + 'm';
    } else if (estimateAmount > 1000) {
      estimateAmount = Math.round(estimateAmount / 100) / 10 + 'k';
    }
    return 'Approx: ' + estimateAmount + ' USD';
  }
  return 'Approx: Unknown amount';
};

var getUSDEstimate = function(amount, denomination, callback) {
  var conv_rate;
  var eth_usd;
  var eth_amount;

  try {
    amount = parseFloat(amount);
  } catch (e) {
    return 'Incorrect amount';
  }
  if (document.conversion_rates && document.conversion_rates[denomination]) {
    conv_rate = document.conversion_rates[denomination];
    return callback(estimate(amount, conv_rate));
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
    return callback(estimate(amount, conv_rate));
  }).fail(function() {
    return callback('Approx: Unknown amount');
  });
};