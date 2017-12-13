var getUSDEstimate = function (amount, denomination) {
    if (document.conversion_rates && document.conversion_rates[denomination]) {
        var usd_amount = amount / document.conversion_rates[denomination];
    } else {
        var request_url = '/sync/get_amount?amount=' + amount + '&denomination=' + denomination;
        jQuery.get(request_url, function (result) {
            var usd_amount = result['usdt'];
            var eth_amount = result['eth'];
            var conv_rate = amount / usd_amount / eth_amount
            //store conv rate for later in cache
            if (typeof document.conversion_rates == 'undefined') {
                document.conversion_rates = {}
            }
            document.conversion_rates[denomination] = conv_rate;
        }).fail(function () {
            return None
        });
    }
    if (usd_amount) {
        usd_amount = Math.round(usd_amount * 100) / 100;
        if (usd_amount > 1000000) {
            usd_amount = Math.round(usd_amount / 100000) / 10 + "m"
        } else if (usd_amount > 1000) {
            usd_amount = Math.round(usd_amount / 100) / 10 + "k"
        }
        return ('Approx: ' + usd_amount + ' USD');
    } else {
        return null;
    }


};