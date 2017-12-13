var estimate= function(amount, conv_rate) {
    var estimateAmount = amount / conv_rate;
    if (estimateAmount) {
        estimateAmount = Math.round(estimateAmount * 100) / 100;
        if (estimateAmount > 1000000) {
            estimateAmount = Math.round(estimateAmount / 100000) / 10 + "m"
        } else if (estimateAmount > 1000) {
            estimateAmount = Math.round(estimateAmount / 100) / 10 + "k"
        }
        return ('Approx: ' + estimateAmount + ' USD');
    } else {
        return null;
    }
};

var getUSDEstimate = function (amount, denomination) {
    var conv_rate;
    var usd_amount;
    var eth_amount;
    try {
        amount = parseFloat(amount);
    } catch (e) {
        return null;
    }

    if (document.conversion_rates && document.conversion_rates[denomination]) {
        conv_rate = document.conversion_rates[denomination]
        return estimate(amount, conv_rate)
    } else {
        var request_url = '/sync/get_amount?amount=' + amount + '&denomination=' + denomination;
        jQuery.get(request_url, function (result) {
            usd_amount = result['usdt'];
            eth_amount = parseFloat(result['eth']);
            conv_rate = (amount/eth_amount)*usd_amount;
            //store conv rate for later in cache
            if (typeof document.conversion_rates == 'undefined') {
                document.conversion_rates = {}
            }
            document.conversion_rates[denomination] = conv_rate;
            return estimate(amount, conv_rate)

        }).fail(function () {
            return null
        });
    }


};