
/**
 * Simple plugin for range slider
 *
 * ex:
 * <input type="range" min="1" max="100" value="50" data-rangeslider="demo">
 * Value: <span id="demo"></span>
 *
*/

(function() {
  this.createRanger = function(slider, id) {
    var output = document.getElementById(id);

    output.innerHTML = slider.value;
    slider.oninput = function() {
      output.innerHTML = this.value;
    };

  };

  this.rangeslider = function() {
    var elem = document.querySelectorAll('[data-rangeslider]');

    for (var i = 0; i < elem.length; ++i) {
      if (elem[i].dataset.rangeslider) {
        createRanger (elem[i], elem[i].dataset.rangeslider);
      }
    }
  };
}());

var rangeslider = new rangeslider();
