/**
 * Simple plugin for truncate the hash at the center
 *
 * ex:
 * <div data-truncatehash="3">1234567891233456789asd</div>
 * <div data-truncatehash>1234567891233456789asd</div>
*/

(function (){
  this.truncate = function(elem,number) {
    var number = !number ? number = 4 : number
    var content = elem.textContent.trim();
    content =  content.substr(0,number+2)+ '\u2026'+ content.substr(-number)
    elem.textContent = content
  }
  
  this.truncateHash = function () {
    var elem = document.querySelectorAll('[data-truncatehash]')
    for (var i = 0; i < elem.length; ++i) {
      new truncate(elem[i],elem[i].dataset.truncatehash)
    }
  }
}())

new truncateHash()  