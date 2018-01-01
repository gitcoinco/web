var internal = 500; 
$(document).ready(function(){
    $('.cards .img img').each(function(){
        internal += 500;
        setTimeout(function(){
            $.get($(this).data('hover'));
        },internal);

        $(this).mouseover(function(){
            $(this).data('og-src',$(this).attr('src'));
            $(this).attr('src',$(this).data('hover'));
        })
        $(this).mouseout(function(){
            $(this).attr('src',$(this).data('og-src'));
        })

    });
});
