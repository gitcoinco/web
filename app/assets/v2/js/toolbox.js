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
  $.fn.isInViewport = function() {
  var elementTop = $(this).offset().top;
  var elementBottom = elementTop + $(this).outerHeight();
  var viewportTop = $(window).scrollTop();
  var viewportBottom = viewportTop + $(window).height();
  return elementBottom > viewportTop && elementTop < viewportBottom;
  };

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
  $(window).scroll(function(){
      var scrollPos = $(document).scrollTop();
      if(parseInt(scrollPos) % 100 < 10){
        $('#toc a').removeClass('active');
        $('#toc a').each(function(){
          var href = $(this).attr('href');
          var target_selector = href;
          if($(target_selector).isInViewport()){
            if($("toc a.active").length < 1){
              $(this).addClass('active');
            }
          }
        });
      }
  });  
});
