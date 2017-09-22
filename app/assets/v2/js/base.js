$(document).ready(function(){

    //get gitcoin modal
    $("a[href='/get']").click(function(e){
      e.preventDefault();
      var url = $(this).attr('href');
      setTimeout(function(){
        $.get(url, function(newHTML){
            $(newHTML).appendTo('body').modal();
        });
      },300);
    });

    //get gitcoin modal
    $("body").delegate('.iama','click', function(){
        document.location.href = $(this).find('a').attr('href');
    });

    //pulse animation on click
    $('.pulseClick').click(function(e){
      var ele = $(this);
      ele.addClass("pulseButton");
      var callback = function(){
        ele.removeClass("pulseButton");
      };
      setTimeout(callback,300);
    });

});

$(window).scroll(function(){
    var scrollPos = $(document).scrollTop();
    //console.log(scrollPos);
});