//helper functions
var sidebar_keys = ['experience_level', 'project_length', 'bounty_type', 'bounty_filter'];

var get_search_URI = function(){
    var uri = '/api/v0.1/bounties?';
    var keywords = $("#keywords").val();
    if(keywords){
        uri += '&raw_data='+keywords;
    }
    for(var i=0;i<sidebar_keys.length;i++){
        var key = sidebar_keys[i];
        var val = $("input[name="+key+"]:checked").val()

        //special casing. TODO: clean this up
        if(key == 'bounty_filter'){
            if(val=='open') {
                uri = uri + 'is_open=True&';
            } else if(val == 'myself'){
                key='bounty_owner_address';
            } else if(val == 'watched'){
                key='github_url';
                val = watch_list();
            } 
        }
        if(val!='any'){
            uri += '&'+key+'='+val;
        }
    }
    if(typeof web3 != 'undefined' && web3.eth.coinbase){
        uri += '&coinbase='+web3.eth.coinbase;
    }

    var selected_option = $('.sort_option.selected');
    var direction = selected_option.data('direction');
    var order_by = selected_option.data('key');
    if(order_by){
        uri += '&order_by='+(direction == "-" ? direction : "")+order_by;
    }

    return uri;
};

var refreshBounties = function(){
    $('.nonefound').css('display', 'none');
    $('.loading').css('display', 'block');
    $('.bounty_row').remove();

    //filter
    var uri = get_search_URI();

    //order
    $.get(uri, function(results){
        if(results.length==0){
            $(".nonefound").css('display','block');
        }
        for(var i = 0; i<results.length; i++){
                //setup
                var result = results[i];
                var related_token_details = tokenAddressToDetails(result['token_address'])
                var decimals = 18;
                if(related_token_details && related_token_details.decimals){
                    decimals = related_token_details.decimals;
                }
                var divisor = 10**decimals;
                result['rounded_amount'] = Math.round(result['value_in_token'] / divisor * 100) / 100;
                var is_expired = new Date(result['expires_date']) < new Date();

                //setup args to go into template
                if(typeof web3 != 'undefined' && web3.eth.coinbase == result['bounty_owner_address']){
                    result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">mine</span></a>';
                } else if(result['claimeee_address'] != '0x0000000000000000000000000000000000000000'){
                    result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">claimed</span></a>';
                } else if(is_on_watch_list(result['github_url'])) {
                    result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">watched</span></a>';
                }
                result['action'] = '/bounty/details?url=' + result['github_url'];
                result['title'] = result['title'] ? result['title'] : result['github_url'];
                result['p'] = timeDifference(new Date(), new Date(result['created_on']))+' - '+(result['project_length'] ? result['project_length'] : "Unknown Length")+' - '+(result['bounty_type'] ? result['bounty_type'] : "Unknown Type")+' - '+(result['experience_level'] ? result['experience_level'] : "Unknown Experience Level") + ( is_expired ? " - (Expired)" : "");
                result['watch'] = 'Watch';
                //render the template
                var tmpl = $.templates("#result");
                var html = tmpl.render(result);

                $("#bounties").append(html);
        }
    }).fail(function(){
        _alert('got an error. please try again, or contact support@gitcoin.co');
    }).always(function(){
        $('.loading').css('display', 'none');
    });        
};

window.addEventListener('load', function() {
    var q = getParam('q');
    if(q){
        $("#keywords").val(q);
    }
    refreshBounties();
});


$(document).ready(function(){

    //index clicks
    $("#bounties").delegate('.bounty_row','click',function(e){
        document.location.href = $(this).data('href');
        e.preventDefault();
    });

    //sidebar clear
    $(".dashboard #clear").click(function(e){
        for(var i=0;i<sidebar_keys.length;i++){
            var key = sidebar_keys[i];
            var val = $("input[name="+key+"][value=any]").prop("checked", true);
        };
        refreshBounties();
        e.preventDefault();
    });

    //search bar
    $("#bounties").delegate('#new_search','click',function(e){
        refreshBounties();
        e.preventDefault();
    });

    $(".search-area input[type=text]").keypress(function(e){
        if(e.which == 13) {
            refreshBounties();
            e.preventDefault();
        }        
    });

    //sidebar filters
    $('.sidebar_search input[type=radio], .sidebar_search label').change(function(e){
        refreshBounties();
        e.preventDefault();
    });

    //sort direction
    $("#bounties").delegate('.sort_option','click',function(e){
        if($(this).hasClass('selected')){
            if($(this).data('direction') == '-'){
                $(this).data('direction', '+')
            } else {
                $(this).data('direction', '-');
            }
        }
        $('.sort_option').removeClass('selected');
        $(this).addClass('selected');
        refreshBounties();
        e.preventDefault();
    });

    //email subscribe functionality
    $(".save_search").click(function(e){
        e.preventDefault();
        $("#save").remove();
        var url = '/search/save';
        setTimeout(function(){
            $.get(url, function(newHTML){
                $(newHTML).appendTo('body').modal();
                $("#save").append("<input type=hidden name=raw_data value='"+get_search_URI()+"'>")
                $('#save_email').focus();
            });
        },300);
    });

    var emailSubscribe = function(){
        var email = $("#save input[type=email]").val();
        var raw_data = $("#save input[type=hidden]").val();
        var is_validated = validateEmail(email);
        if(!is_validated){
             _alert({ message: "Please enter a valid email address." });
        } else {
            var url = '/search/save';
            $.post(url, {
                email: email,
                raw_data, raw_data,
            }, function(response){
                var status = response['status'];
                if(status == 200){
                     _alert({ message: "Success!"},'success');
                     $.modal.close();
                } else {
                     _alert({ message: response['msg']});
                }
            });
        }
    }

    $("body").delegate("#save input[type=email]", 'keypress', function(e){
        if(e.which == 13) {
            emailSubscribe();
            e.preventDefault();
        }        
    });
    $("body").delegate("#save a.btn-darkBlue", 'click', function(e){
        emailSubscribe();
        e.preventDefault();
    });


});