$(document).ready(function(){
    $('.cards .img img').each(function(){
        $(this).mouseover(function(){
            $(this).data('og-src',$(this).attr('src'));
            $(this).attr('src',$(this).data('hover'));
        })
        $(this).mouseout(function(){
            $(this).attr('src',$(this).data('og-src'));
        })

    });
});
