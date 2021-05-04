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

    if (elem && elem.textContent === undefined) {
      let content = elem.trim();

      content = content.substr(0, number + 2) + '\u2026' + content.substr(-number);
      return (this.elem = content);
    }
    let content = !elem ? '' : elem.textContent.trim();

    content = content.substr(0, number + 2) + '\u2026' + content.substr(-number);
    if (elem)
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
