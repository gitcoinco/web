/* eslint-disable no-new */
/* eslint-disable no-console */

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
    const elem = document.querySelectorAll('[data-truncatehash]');

    for (let i = 0; i < elem.length; ++i) {
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
    const address = !_address ? _address = web3.eth.coinbase : _address;

    if (elem.nodeName == 'INPUT') {
      elem.value = address;
    } else {
      elem.textContent = address;
      elem.setAttribute('title', address);
    }
    new truncateHash();
  };

  this.metamaskAddress = function() {
    try {
      const currentWallet = web3.eth.coinbase;
      const elem = document.querySelectorAll('[data-metamask-address]');
  
      for (let i = 0; i < elem.length; ++i) {
        new getaddress(elem[i], currentWallet);
      }
    } catch (ignore) {
      console.log('%c error: web3 not defined. ensure metamask is installed & unlocked', 'color: red');
    }
  };
}());

new metamaskAddress();

try {
  web3.currentProvider.publicConfigStore.on('update', function(e) {
    new metamaskAddress();
  });
} catch (ignore) {
  console.log('%c error: web3 not defined. ensure metamask is installed & unlocked', 'color: red');
}
