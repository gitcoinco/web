// Wait until page is loaded, then run the function
$(document).ready(function() {
  var gasLimitEstimate = 0;
  // new new funding page

  if (document.location.href.indexOf('issue/fulfill') != -1) {
    gasLimitEstimate = 207103;
  }
  // new fulfill funding page
  if (document.location.href.indexOf('/new') != -1) {
    gasLimitEstimate = 318730;
  }
  // new fulfill funding page
  if (document.location.href.indexOf('issue/increase') != -1) {
    gasLimitEstimate = 56269;
  }
  // new process funding page
  if (document.location.href.indexOf('issue/accept') != -1) {
    gasLimitEstimate = 103915;
  }
  // new kill funding page
  if (document.location.href.indexOf('issue/cancel') != -1) {
    gasLimitEstimate = 67327;
  }

  var estimateGas = function(success_callback, failure_callback, final_callback) {
    // TODO: could do a web3 .estimateGas()
    success_callback(gasLimitEstimate, gasLimitEstimate, '');
    final_callback();
  };
  // updates recommended metamask settings
  var updateInlineGasEstimate = function() {
    var success_callback = function(gas, gasLimit, _) {
      $('#gasLimit').val(parseInt(gas));
      update_metamask_conf_time_and_cost_estimate();
    };
    var failure_callback = function(errors) {
      $('#gasLimit').val('Unknown');
      update_metamask_conf_time_and_cost_estimate();
    };
    var final_callback = function() {
      // …
    };

    estimateGas(success_callback, failure_callback, final_callback);
  };

  setTimeout(function() {
    updateInlineGasEstimate();
  }, 500);
  $('input').change(updateInlineGasEstimate);
  $('#gasPrice').keyup(update_metamask_conf_time_and_cost_estimate);


});
