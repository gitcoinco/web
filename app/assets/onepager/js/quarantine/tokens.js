/* eslint-disable nonblock-statement-body-position */

var tokenAddressToDetails = function(addr) {
  var _tokens = tokens(document.web3network);

  for (var i = 0; i < _tokens.length; i += 1) {
    if (_tokens[i].addr == addr) {
      return _tokens[i];
    }
  }
  return null;
};
