var retrieveAmount = function() {
  var ele = jQuery('input[amount]');
  var target_ele = jQuery('#usd_amount');

  if (target_ele.html() == '') {
    target_ele.html('<img style="width: 50px; height: 50px;" src=/static/v2/images/loading_v2.gif>');
  }

  var amount = jQuery('input[name=amount]').val();
  var denomination = 'ETH';
  var request_url = '/sync/get_amount?amount=' + amount;

  // use cached conv rate if possible.
  if (document.conversion_rates && document.conversion_rates.ETH) {
    var usd_amount = amount / document.conversion_rates.ETH;

    updateAmountUI(target_ele, usd_amount);
    return;
  }

  // if not, use remote one
  jQuery.get(request_url, function(result) {

    // update UI
    var usd_amount = result.usdt;
    var conv_rate = amount / usd_amount;

    updateAmountUI(target_ele, usd_amount);

    // store conv rate for later in cache
    if (typeof document.conversion_rates == 'undefined') {
      document.conversion_rates = {};
    }
    document.conversion_rates.ETH = conv_rate;

  }).fail(function() {
    target_ele.html(' ');
  });
};

var updateAmountUI = function(target_ele, usd_amount) {
  usd_amount = Math.round(usd_amount * 100) / 100;

  if (usd_amount > 1000000) {
    usd_amount = Math.round(usd_amount / 100000) / 10 + 'm';
  } else if (usd_amount > 1000) {
    usd_amount = Math.round(usd_amount / 100) / 10 + 'k';
  }
  target_ele.html('Approx: ' + usd_amount + ' USD');
};
