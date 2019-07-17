// Wait until page is loaded, then run the function

var gas_amount = function(page_url) {
  var gasLimitEstimate = 0;
  // new new funding page

  if (page_url.indexOf('issue/fulfill') != -1) {
    gasLimitEstimate = 207103;
  } else if (page_url.indexOf('grants/new') != -1) { // new grant contribution
    gasLimitEstimate = 3000000;
  } else if (page_url.indexOf('/new') != -1) { // new fulfill funding page
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('issue/increase') != -1) { // new fulfill funding page
    gasLimitEstimate = 56269;
  } else if (page_url.indexOf('issue/accept') != -1) { // new process funding page
    gasLimitEstimate = 103915;
  } else if (page_url.indexOf('issue/cancel') != -1) { // new kill funding page
    gasLimitEstimate = 67327;
  } else if (page_url.indexOf('issue/advanced_payout') != -1) { // advanced payout page
    gasLimitEstimate = 67327;
  } else if (page_url.indexOf('issue/payout') != -1) { // bulk payout
    gasLimitEstimate = 103915;
  } else if (page_url.indexOf('tip/send') != -1) { // tip
    gasLimitEstimate = 21000;
  } else if (page_url.indexOf('tip/receive') != -1) { // tip
    gasLimitEstimate = 21000;
  } else if (page_url.indexOf('subscription') != -1) { // subscribe grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('grants/fund') != -1) { // fund grant contribution
    gasLimitEstimate = 69169;
  } else if (page_url.indexOf('grants/cancel') != -1) { // cancel grant contribution
    gasLimitEstimate = 45805;
  } else if (page_url.indexOf('grants/') != -1) { // cancel grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('/fund') != -1) { // grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('subscribe') != -1) { // gitcoin subscription plans
    gasLimitEstimate = 318730;
  }
  return gasLimitEstimate;
};

jQuery(document).ready(function() {

  var gasLimitEstimate = gas_amount(document.location.href);

  var estimateGas = function(success_callback, failure_callback, final_callback) {
    // TODO: could do a web3 .estimateGas()
    success_callback(gasLimitEstimate, gasLimitEstimate, '');
    final_callback();
  };
  // updates recommended metamask settings
  var updateInlineGasEstimate = function() {
    var success_callback = function(gas, gasLimit, _) {
      jQuery('#gasLimit').val(parseInt(gas));
      update_metamask_conf_time_and_cost_estimate();
    };
    var failure_callback = function(errors) {
      jQuery('#gasLimit').val('Unknown');
      update_metamask_conf_time_and_cost_estimate();
    };
    var final_callback = function() {
      // …
    };

    estimateGas(success_callback, failure_callback, final_callback);
  };

  // only check for updating gas estimates IFF we're on a page where
  // update_metamask_conf_time_and_cost_estimate() is defined
  if (typeof update_metamask_conf_time_and_cost_estimate != 'undefined') {
    setTimeout(function() {
      updateInlineGasEstimate();
    }, 500);
    jQuery('input').change(updateInlineGasEstimate);
    jQuery('#gasPrice').keyup(update_metamask_conf_time_and_cost_estimate);
  }


});
