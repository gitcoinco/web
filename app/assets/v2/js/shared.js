// helper functions
var callFunctionWhenTransactionMined = function(txHash, f){
    var transactionReceipt = web3.eth.getTransactionReceipt(txHash, function(error, result){
        if(result){
            f();
        } else {
            setTimeout(function(){
                callFunctionWhenTransactionMined(txHash, f);
            },1000);
        }
    });
};

var _alert = function (msg, _class){
    if(typeof msg == 'string'){
        msg = {
            'message': msg
        }
    }
    var numAlertsAlready = $('.alert:visible').length;
    var top = numAlertsAlready * 66;
    var html = '    <div class="alert '+_class+'" style="top: '+top+'px"> \
      <span class="closebtn" >&times;</span> \
      <strong>' + (typeof msg['title'] != 'undefined' ? msg['title'] : '') + '</strong>\
      ' + msg['message'] + '\
    </div> \
';
    $('body').append(html);
}

var timestamp = function(){
    return Math.floor(Date.now() / 1000);
};

var watch_list = function(){
    if(typeof localStorage['watches'] == 'undefined'){
        return [];
    }
    return localStorage['watches'].split(',');
}

var is_on_watch_list = function(issueURL){
    if(localStorage['watches'].indexOf(issueURL) != -1){
        return true;
    }
    return false;
}

var add_to_watch_list = function(issueURL){
    if(is_on_watch_list(issueURL)){
        return;
    }
    localStorage['watches'] = localStorage['watches'] + "," + issueURL;
}

var remove_from_watch_list = function(issueURL){
    if(!is_on_watch_list(issueURL)){
        return;
    }
    localStorage['watches'] = localStorage['watches'].replace("," + issueURL,"");
}

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function getParam(parameterName) {
    var result = null,
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
          tmp = item.split("=");
          if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    return result;
}

function timeDifference(current, previous) {

    if(current<previous){
        return "in " + timeDifference(previous, current).replace(" ago","")
    }

    var msPerMinute = 60 * 1000;
    var msPerHour = msPerMinute * 60;
    var msPerDay = msPerHour * 24;
    var msPerMonth = msPerDay * 30;
    var msPerYear = msPerDay * 365;

    var elapsed = current - previous;

    if (elapsed < msPerMinute) {
         return Math.round(elapsed/1000) + ' seconds ago';   
    }

    else if (elapsed < msPerHour) {
         return Math.round(elapsed/msPerMinute) + ' minutes ago';   
    }

    else if (elapsed < msPerDay ) {
         return Math.round(elapsed/msPerHour ) + ' hours ago';   
    }

    else if (elapsed < msPerMonth) {
        return Math.round(elapsed/msPerDay) + ' days ago';   
    }

    else if (elapsed < msPerYear) {
        return Math.round(elapsed/msPerMonth) + ' months ago';   
    }

    else {
        return Math.round(elapsed/msPerYear ) + ' years ago';   
    }
}

var sync_web3 = function(issueURL){
    var url = '/bounty/sync_web3';
    args = {
        'issueURL': issueURL,
    }
    $.post(url, args, function(){
        console.log('done');
    })
}


//sidebar
$(document).ready(function(){

    $('.sidebar_search input[type=radio], .sidebar_search label').change(function(e){
        if(document.location.href.indexOf("/dashboard") == -1 && document.location.href.indexOf("/explorer") == -1){
            document.location.href = '/explorer';
            e.preventDefault();
        }
    });

    $("body").delegate(".alert .closebtn", 'click', function(e){
        $(this).parents('.alert').remove();
        $('.alert').each(function(){
            var old_top = $(this).css('top');
            var new_top = (parseInt(old_top.replace('px')) - 66) + 'px';
            $(this).css('top', new_top);
        });
    });
});

//callbacks that can retrieve various metadata about a github issue URL
var retrieveTitle = function(){
    var ele = $("input[name=issueURL]");
    var target_ele = $("input[name=title]");
    var issue_url = ele.val();
    if(typeof issue_url == 'undefined'){
        return;
    }
    if(issue_url.length < 5 || issue_url.indexOf('github') == -1){
        return;
    }
    var request_url = '/helpers/get_title?url=' + encodeURIComponent(issue_url);
    target_ele.addClass('loading');
    $.get(request_url, function(result){
        target_ele.removeClass('loading');
        if(result['title']){
            target_ele.val(result['title']);
        }
    });
};
var retrieveKeywords = function(){
    var ele = $("input[name=issueURL]");
    var target_ele = $("input[name=keywords]");
    var issue_url = ele.val();
    if(typeof issue_url == 'undefined'){
        return;
    }
    if(issue_url.length < 5 || issue_url.indexOf('github') == -1){
        return;
    }
    var request_url = '/helpers/get_keywords?url=' + encodeURIComponent(issue_url);
    target_ele.addClass('loading');
    $.get(request_url, function(result){
        target_ele.removeClass('loading');
        if(result['keywords']){
            var keywords = result['keywords'];
            target_ele.val(keywords.join(', '));
        }
    });
};


//figure out what version of web3 this is
window.addEventListener('load', function() {
    var timeout_value = 50;
    setTimeout(function(){
        if (typeof web3 =='undefined'){
            $("#sidebar_head").html("Web3 disabled <img src='/static/v2/images/icons/question.png'>");
            $("#sidebar_p").html("Please install <a target=new href=https://chrome.google.com/webstore/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn?hl=en> Metamask</a>. ");
        } else if (typeof web3.eth.accounts[0] =='undefined'){
            $("#sidebar_head").html("Web3 locked <img src='/static/v2/images/icons/lock.png'>");
            $("#sidebar_p").html("Please unlock <a target=new href=https://chrome.google.com/webstore/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn?hl=en> Metamask</a>. ");
        } else {
            web3.version.getNetwork((error, netId) => {
                if(!error){
                    var network = "unknown";
                      switch (netId) {
                        case "1":
                          network = 'mainnet';
                          break
                        case "2":
                          network = 'morden';
                          break
                        case "3":
                          network = 'ropsten';
                          break
                        default:
                          network = "custom network";
                      }
                    document.web3network = network;
                    $("#sidebar_head").html("Web3 enabled <img src='/static/v2/images/icons/rss.png'>");
                    $("#sidebar_p").html("Connected to " + network + ".");
                }
                else {
                    $("#sidebar_head").html("Web3 disabled");
                    $("#sidebar_p").html("Please install & nlock <a target=new href=https://chrome.google.com/webstore/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn?hl=en> Metamask</a>. ");
                }
            })
        }
    }, timeout_value);

    setTimeout(function(){
        //detect web3, and if not, display a form telling users they must be web3 enabled.
        if($("#primary_form").length){
            if(typeof web3 == 'undefined'){
                $("#no_metamask_error").css('display', 'block');
                $("#primary_form").remove();
                return;
            } else {
                if(!web3.eth.coinbase){
                    $("#unlock_metamask_error").css('display', 'block');
                    $("#primary_form").remove();
                    return;
                }
                web3.eth.getBalance(web3.eth.coinbase, function(errors,result){
                    var balance = result.toNumber();
                    if(balance == 0){
                        $("#zero_balance_error").css('display', 'block');
                        $("#primary_form").remove();
                    }
                });
            };
        }
    }, timeout_value);

});
