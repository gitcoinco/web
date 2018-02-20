//preloading all images on a small interval
var interval = 500;
document.preloads = [];
setInterval(function(){
    if(document.preloads.length){
        var url = document.preloads.pop();
        $.get(url);
    }
},interval);

$(document).ready(function(){
    $('.cards .img img').each(function(){
        document.preloads.push($(this).data('hover'));
        $(this).mouseover(function(){
            $(this).data('og-src',$(this).attr('src'));
            $(this).attr('src',$(this).data('hover'));
        })
        $(this).mouseout(function(){
            $(this).attr('src',$(this).data('og-src'));
        })

    });
});
