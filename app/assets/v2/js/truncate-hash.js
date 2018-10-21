/* eslint-disable no-new */

/**
 * Simple plugin for truncate the hash at the center
 *
 * ex:
 * <div data-truncatehash="3">1234567891233456789asd</div>
 * <div data-truncatehash>1234567891233456789asd</div>
 * new truncate('123456789')
*/

(function() {
  this.truncate = function(elem, _number) {
    var number = !_number ? _number = 4 : _number;

    if (elem.textContent === undefined) {
      let content = elem.trim();

      content = content.substr(0, number + 2) + '\u2026' + content.substr(-number);
      return (this.elem = content);
    }
    let content = elem.textContent.trim();

    content = content.substr(0, number + 2) + '\u2026' + content.substr(-number);
    elem.textContent = content;
  };

  this.truncateHash = function() {
    var elem = document.querySelectorAll('[data-truncatehash]');

    for (var i = 0; i < elem.length; ++i) {
      new truncate(elem[i], elem[i].dataset.truncatehash);
    }
  };
}());

new truncateHash();


/**
 * Get address form metamask
 *
 * ex:
 * <div data-metamask-address>1234567891233456789asd</div>
*/
(function() {
  this.getaddress = function(elem, _address) {
    var address = !_address ? _address = web3.eth.coinbase : _address;

    if (elem.nodeName == 'INPUT') {
      elem.value = address;
    } else {
      elem.textContent = address;
      elem.setAttribute('title', address);
    }
    new truncateHash();
  };

  this.metamaskAddress = function() {
    var currentWallet = web3.eth.coinbase;

    var elem = document.querySelectorAll('[data-metamask-address]');
    // var elem = $('#wallet-address')

    for (var i = 0; i < elem.length; ++i) {
      new getaddress(elem[i], currentWallet);
    }
  };
}());
new metamaskAddress();

web3.currentProvider.publicConfigStore.on('update', function(e) {
  new metamaskAddress();
});