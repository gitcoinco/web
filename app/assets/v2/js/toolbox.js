// preloading all images on a small interval
var interval = 500;

document.preloads = [];

setInterval(function() {
  if (document.preloads.length) {
    var url = document.preloads.pop();

    $.get(url);
  }
}, interval);

$(document).ready(function() {
  $('.cards .img img').each(function(index, element) {
    document.preloads.push($(element).data('hover'));

    $(element).mouseover(function() {
      $(element).data('og-src', $(element).attr('src'));
      $(element).attr('src', $(element).data('hover'));
    });

    $(element).mouseout(function() {
      $(element).attr('src', $(element).data('og-src'));
    });
  });
});
