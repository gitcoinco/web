$(document).ready(function(){
    var base_url = '/quadraticlands/mission/postcard/svg?';
    var $target = $("#target");
    $('#text').keyup(function(){
        update_output();
    });
    $('.backgrounds li').click(function(){
        $(this).parents('.parent').find('li').removeAttr("selected")
        $(this).attr("selected", "selected");
        update_output();
    });
    var update_output = function(){
        var text = $("#text").val();
        text = text.replace( /[\r\n]/gm, " NEWLINE " );
        var selected = $('li[selected=selected]');
        var attrs = `&text=${text}`;
        for(var i=0;i<selected.length;i++){
            console.log(selected[i]);
            var key = $(selected[i]).attr('name');
            var val = $(selected[i]).attr('value');
            attrs += `&${key}=${val}`;

        }
        var url = base_url + attrs;
        console.log(url);
        $target.attr("src", url);
    };
    update_output();
});;