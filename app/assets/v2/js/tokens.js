
var tokenAddressToDetails = function(addr) {
  return tokenAddressToDetailsByNetwork(addr, document.web3network);
};

var tokenAddressToDetailsByNetwork = function(addr, network) {
  var _tokens = tokens(network);

  for (var i = 0; i < _tokens.length; i += 1) {
    if (_tokens[i].addr && addr) {
      if (_tokens[i].addr.toLowerCase() == addr.toLowerCase()) {
        return _tokens[i];
      }
    }
  }
  return null;
};

/**
 * Retrieve token details
 * @param {*} network [string]
 * @param {*} token_name [string]
 */
const tokenNameToDetails = (network, token_name) => {
  var _tokens = tokens(network);

  return _tokens.filter(_token => _token.name == token_name)[0];
};

var load_tokens = function() {
  window.addEventListener('load', function() {
    waitforWeb3(function() {
      // add tokens to the submission form
      var tokenAddress = localStorage['tokenAddress'];

      if (!tokenAddress) {
        tokenAddress = '0x0000000000000000000000000000000000000000';
      }
      var _tokens = tokens(document.web3network);

      for (var i = 0; i < _tokens.length; i++) {
        if (_tokens[i]['divider']) {
          $('select[name=denomination]').append('<option disabled />');
          continue;
        }

        var token = _tokens[i];
        var select = {
          value: token['addr'],
          text: token['name']
        };

        if (token['addr'] == tokenAddress) {
          select['selected'] = 'selected';
        }

        $('select[name=denomination]').append($('<option>', select));
      }
      // if web3, set the values of some form variables
      var url_string = window.location.href;
      var url = new URL(url_string);
      var params_amount = url.searchParams.get('amount');

      if (typeof localStorage['amount'] != 'undefined') {
        if (params_amount != null) {
          if (localStorage['amount'] != params_amount) {
            localStorage.setItem('amount', params_amount);
            $('input[name=amount]').val(params_amount);
          }
        } else {
          $('input[name=amount]').val(localStorage['amount']);
        }
      }
      if (typeof localStorage['githubUsername'] != 'undefined') {
        if (!$('input[name=githubUsername]').val()) {
          $('input[name=githubUsername]').val(localStorage['githubUsername']);
        }
      }
      if (typeof localStorage['notificationEmail'] != 'undefined') {
        $('input[name=notificationEmail]').val(localStorage['notificationEmail']);
      }
    });
  });
};
