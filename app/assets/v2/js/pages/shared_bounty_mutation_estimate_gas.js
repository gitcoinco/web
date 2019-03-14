// Wait until page is loaded, then run the function

var gas_amount = function(page_url) {
  var gasLimitEstimate = 0;
  // new new funding page

  if (page_url.includes('issue/fulfill')) {
    gasLimitEstimate = 207103;
  } else if (page_url.includes('/new')) { // new fulfill funding page
    gasLimitEstimate = 318730;
  } else if (page_url.includes('issue/increase')) { // new fulfill funding page
    gasLimitEstimate = 56269;
  } else if (page_url.includes('issue/accept')) { // new process funding page
    gasLimitEstimate = 103915;
  } else if (page_url.includes('issue/cancel')) { // new kill funding page
    gasLimitEstimate = 67327;
  } else if (page_url.includes('issue/advanced_payout')) { // advanced payout page
    gasLimitEstimate = 67327;
  } else if (page_url.includes('issue/payout')) { // bulk payout
    gasLimitEstimate = 103915;
  } else if (page_url.includes('tip/send')) { // tip
    gasLimitEstimate = 21000;
  } else if (page_url.includes('tip/receive')) { // tip
    gasLimitEstimate = 21000;
  } else if (page_url.includes('subscription')) { // cancel grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.includes('grants/new')) { // cancel grant contribution
    gasLimitEstimate = 3000000;
  } else if (page_url.includes('grants/fund')) { // cancel grant contribution
    gasLimitEstimate = 69169;
  } else if (page_url.includes('grants/cancel')) { // cancel grant contribution
    gasLimitEstimate = 45805;
  } else if (page_url.includes('grants/')) { // cancel grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.includes('/fund')) { // grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.includes('subscribe')) { // gitcoin subscription plans
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
