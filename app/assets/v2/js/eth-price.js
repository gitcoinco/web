/**
 * Transform eth to usd
 *
 * ex:
 * <span data-ethprice="0.006">0.006 ETH <small></small></span>
 * The eth value inside data attr will be converted and added to the <small> tag
 * NOTE: needs amount.js to be loaded
 *
*/

(function() {
  this.ethprice = function() {
    var elems = document.querySelectorAll('[data-ethprice]');

    elems.forEach(function(elem) {
      new Promise(function(resolve, reject) {
        getUSDEstimate(elem.dataset.ethprice, 'ETH', function(usdAmount) {
          resolve(usdAmount);
        });
      }).then(function(result) {
        addValue(elem, result);
      }, function(reject) {
        console.log(reject);
      });
    });

    function addValue(elem, result) {
      elem.children[0].textContent = `(${result.value} USD)`;
    }
  };
}());

var ethprice = new ethprice();
