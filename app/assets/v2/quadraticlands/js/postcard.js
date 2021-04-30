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

    if(getParam('text')){
        var ele = getParam('text');
        ele = ele.replaceAll(" NEWLINE ", "\n" );
        $("#text").val(ele);
    }
    var targets = ['front_background', 'back_background', 'front_frame'];
    for(var i=0;i<targets.length; i++){
        var target = targets[i];
        if(getParam(target)){
            var ele = getParam(target);
            var target = $('.backgrounds li[name='+target+'][value=' + ele + ']')
            target.parents('.parent').find('li').removeAttr("selected")
            target.attr("selected", "selected");
        }
    }



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
        $target.attr("src", url);

        window.history.pushState('', 'QL Postcard Generator', '?' + attrs);
    };
    update_output();
});;