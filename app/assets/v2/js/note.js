$(document).ready(function() {
    var startX = null;
    var startY = null;
    var movementStrength = 25;
    var height = movementStrength / $(window).height();
    var width = movementStrength / $(window).width();
    $(".header, .white-light-bg").each(function(){
          var ele = $(this);
          ele.mousemove(function(e){
                var pageX = e.pageX - ($(window).width() / 2);
                var pageY = e.pageY - ($(window).height() / 2);
                var newvalueX = width * (pageX - startX) * -1 - 25;
                var newvalueY = height * (pageY - startY) * -1 - 50;
                if(!startX){
                  startX = newvalueX;
                }
                if(!startY){
                  startY = newvalueY;
                }
                ele.css("background-position", (newvalueX - startX)+"px     "+(newvalueY - startY)+"px");
          });
    });
});