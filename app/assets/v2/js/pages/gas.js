jQuery(document).ready(function() {

  var gas_price_to_confirmation_time = function(gas_price) {
    if (typeof gas_times == 'undefined') {
      return;
    }
    for (var i = 0; i < gas_times.length; i++) {
      var d = gas_times[i];

      if (gas_price < (parseInt(d[0]) + 0.1) && gas_price > (parseInt(d[0]) - 0.1)) {
        return d[1];
      }
    }
    return 'n/a';
  };

  // bindings
  jQuery('.target').each(function() {
    var target = jQuery(this).val();

    jQuery(this).parents('tr').find('.gas_needed').val(gas_amount(target));
  });
  jQuery('.gas_cost').keyup(function() {
    var gas_price_gwei = jQuery(this).val();

    update_table(gas_price_gwei);
  });

  // updates the gas predictor table
  var update_table = function(gas_price_gwei) {
    var wei_to_gwei = 10 ** 9;
    var wei_to_eth = 10 ** 18;
    var conf_time = gas_price_to_confirmation_time(gas_price_gwei);
    var eth_to_usd = document.eth_to_usd;

    jQuery('#estimateTable tr').each(function() {
      var gas_needed = jQuery(this).find('.gas_needed').val();
      var eth_cost = 1.0 * gas_price_gwei * gas_needed * wei_to_gwei / wei_to_eth;
      var usd_cost = Math.round(eth_to_usd * eth_cost * 100) / 100;

      jQuery(this).find('.total_cost_eth').val(eth_cost);
      jQuery(this).find('.total_cost_usd').val(usd_cost);
      jQuery(this).find('.total_time').val(conf_time);
    });
  };

  // initial pageload
  var starting_gas_cost = jQuery('.gas_cost').val();

  update_table(starting_gas_cost);
});
