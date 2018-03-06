var _truthy = function(val){
    if(!val){
        return false;
    }
    if(val=='0x0000000000000000000000000000000000000000'){
        return false;
    }
    return true;
}
var address_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a target=new href=https://etherscan.io/address/"+val+">"+val+"</a>"];
    };
var gitcoin_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a target=new href=https://gitcoin.co/profile/"+val+">@"+val.replace('@','')+"</a>"];
    };
var email_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a href=mailto:"+val+">"+val+"</a>"];
    };
var hide_if_empty = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, val];
    };
var unknown_if_empty = function(key, val, result){
        if(!_truthy(val)){
            return [key, 'Unknown']
        }
        return [ key, val];
    };
var link_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a taget=new href="+val+">"+val+"</a>"];
    };

//rows in the 'about' page
var rows = [
    'avatar_url',
    'title',
    'github_url',
    'value_in_token',
    'value_in_eth',
    'value_in_usdt',
    'token_value_in_usdt',
    'web3_created',
    'status',
    'bounty_owner_address',
    'bounty_owner_email',
    'issue_description',
    'bounty_owner_github_username',
    'fulfillments',
    'experience_level',
    'project_length',
    'bounty_type',
    'expires_date',
]
var heads = {
    'avatar_url': 'Issue',
    'value_in_token': 'Issue Funding Info',
    'bounty_owner_address': 'Funder',
    'fulfiller_address': 'Submitter',
    'experience_level': 'Meta',
}
var callbacks = {
    'github_url': link_ize,
    'value_in_token': function(key, val, result){
        return [ 'amount', Math.round((parseInt(val) / Math.pow(10, document.decimals)) * 1000) / 1000 + " " + result['token_name']];
    },
    'avatar_url': function(key, val, result){
        return [ 'avatar', '<a href="/profile/'+result['org_name']+'"><img class=avatar src="'+val+'"></a>'];
    },
    'status': function(key, val, result){
        var ui_status = val;
        if(ui_status=='open'){
            ui_status = '<span style="color: #47913e;">open</span>';
        }
        if(ui_status=='started'){
            ui_status = '<span style="color: #3e00ff;">work started</span>';
        }
        if(ui_status=='submitted'){
            ui_status = '<span style="color: #3e00ff;">work submitted</span>';
        }
        if(ui_status=='done'){
            ui_status = '<span style="color: #0d023b;">done</span>';
        }
        if(ui_status=='cancelled'){
            ui_status = '<span style="color: #f9006c;">cancelled</span>';
        }
        return [ 'status', ui_status];
    },
    'issue_description': function(key, val, result){
        var converter = new showdown.Converter();
        var max_len = 1000;
        val = val.replace(/script/ig,'scr_i_pt');
        var ui_body = val;
        if(ui_body.length > max_len){
            ui_body = ui_body.substring(0, max_len) + '... <a target=new href="'+result['github_url']+'">See More</a> '
        }
        ui_body = converter.makeHtml(ui_body);

        return [ 'issue_description', ui_body];
    },
    'bounty_owner_address': address_ize,
    'bounty_owner_email': email_ize,
    'experience_level': unknown_if_empty,
    'project_length': unknown_if_empty,
    'bounty_type': unknown_if_empty,
    'bounty_owner_github_username': gitcoin_ize,
    'value_in_eth': function(key, val, result){
        if(result['token_name'] == 'ETH' || val == null){
            return [null, null];
        }
        return [ "Amount (ETH)" , Math.round((parseInt(val) / 10**18) * 1000) / 1000];
    },
    'value_in_usdt': function(key, val, result){
        if(val == null){
            return [null, null];
        }
        return [ "Amount_usd" , val];
    },
    'token_value_in_usdt': function(key, val, result){
        if(val == null){
            $('#value_in_usdt_wrapper').addClass('hidden');
            return [null, null];
        }
        return [ "Token_amount_usd" , "$" + val + "/" + result['token_name']];
    },
    'web3_created': function(key, val, result){
        return [ "updated" , timeDifference(new Date(result['now']), new Date(result['created_on']))];
    },
    'expires_date': function(key, val, result){
        var label = "expires";
        expires_date = new Date(val);
        now = new Date(result['now']);
        var response = timeDifference(now, expires_date);
        if( new Date(val) < new Date()){
            label = "expired";
            if(result['is_open']){
                response = "<span title='This issue is past its expiration date, but it is still active.  Check with the submitter to see if they still want to see it fulfilled.'>"+response+"</span>";
            }
        }
        return [ label , response];
    },

}

var isBountyOwner = function(result) {
    var bountyAddress = result['bounty_owner_address']
    return (typeof web3 != 'undefined' && (web3.eth.coinbase == bountyAddress))
}

var showWarningMessage = function (txid) {

    var title_text = $('title').text();
    title_text = '(...)' + title_text;
    $('title').text(title_text);

    if (typeof txid != 'undefined' && txid.indexOf('0x') != -1) {
        clearInterval(interval);
        var link_url = etherscan_tx_url(txid);
        $('#pending_changes').attr("href", link_url);
        $('#transaction_url').attr("href", link_url);
    }

    $(".left-rails").hide();
    $("#bounty_details").hide();
    $("#bounty_detail").hide();

    $(".transaction-status").show();
    $(".waiting_room_entertainment").show();

    var radioButtons = $(".sidebar_search input");

    for (var i = radioButtons.length - 1; i >= 0; i--) {
        radioButtons[i].disabled = true;
    }

    var secondsBetweenQuoteChanges = 30;
    waitingRoomEntertainment();
    var interval = setInterval(waitingRoomEntertainment, secondsBetweenQuoteChanges * 1000);
};

var wait_for_tx_to_mine_and_then_ping_server = function(){
    console.log('checking for updates');
    if(typeof document.pendingIssueMetadata != 'undefined'){
        var txid = document.pendingIssueMetadata['txid'];
        console.log('waiting for web3 to be available');
        callFunctionWhenweb3Available(function(){
            console.log('waiting for tx to be mined');
            callFunctionWhenTransactionMined(txid,function(){
                console.log('tx mined');
                var data = {
                    url: document.issueURL,
                    txid: txid,
                    network: document.web3network,
                }
                var error = function(response){
                    //refresh upon error
                    document.location.href = document.location.href;
                }
                var success = function(response){
                    if(response.status == "200"){
                        console.log("success from sync/web", response);

                        // clear local data
                        localStorage[document.issueURL] = "";
                        document.location.href = document.location.href;
                    } else {
                        console.log("error from sync/web", response);
                        error(response);
                    }
                }
                console.log('syncing gitcoin with web3');
                var uri = "/sync/web3/"
                $.ajax({
                  type: "POST",
                  url: uri,
                  data: data,
                  success: success,
                  error: error,
                  dataType: 'json'
                });
            });
        });
    }
};

var attach_work_actions = function(){
        $("body").delegate('a[href="/interested"], a[href="/uninterested"]', 'click', function (e) {
        e.preventDefault();
        if ($(this).attr('href') == '/interested') {
            $(this).attr('href', '/uninterested');
            $(this).find('span').text('Stop Work');
            add_interest(document.result['pk']);
        } else {
            $(this).attr('href', '/interested');
            $(this).find('span').text('Start Work');
            remove_interest(document.result['pk']);
        }
    });
}

var build_detail_page = function(result){

    //setup
    var decimals = 18;
    var related_token_details = tokenAddressToDetails(result['token_address'])
    if(related_token_details && related_token_details.decimals){
        decimals = related_token_details.decimals;
    }
    document.decimals = decimals;
    $("#bounty_details").css('display','flex');

    // title
    result['title'] = result['title'] ? result['title'] : result['github_url'];
    result['title'] = result['network'] != 'mainnet' ? "(" + result['network'] + ") " + result['title'] : result['title'];
    $('.title').html("Funded Issue Details: " + result['title']);

    //insert table onto page
    for(var j=0; j< rows.length; j++){
        var key = rows[j];
        var head = null;
        var val = result[key];
        if(heads[key]){
            head = heads[key];
        }
        if(callbacks[key]){
            _result = callbacks[key](key, val, result);
            val = _result[1];
        }
        var entry = {
            'head': head,
            'key': key,
            'val': val,
        }
        var id = '#' + key;
        if($(id).length){
            $(id).html(val);
        }
    }

};

var do_actions = function(result){

// Find interest information
pull_interest_list(result['pk'], function(is_interested){

    //actions
    var actions = [];
    if(result['github_url'].substring(0,4) == 'http'){

        var github_url = result['github_url'];

        // hack to get around the renamed repo for piper's work.  can't change the data layer since blockchain is immutable
        github_url = github_url.replace('pipermerriam/web3.py','ethereum/web3.py');

        if(result['github_comments']){
            var entry_comment = {
              href: github_url,
              text: result['github_comments'],
              target: 'new',
              parent: 'right_actions',
              color: 'github-comment'
            };
            actions.push(entry_comment);
        }

        var entry = {
            href: github_url,
            text: 'View on Github',
            target: 'new',
            parent: 'right_actions',
            color: 'darkBlue',
            title: 'Github is where the issue scope lives.  Its also a great place to collaborate with, and get to know, other developers (and sometimes even the repo maintainer themselves!).'
        }

        actions.push(entry);
    }

    if(result['status']=='open' || result['status']=='started' || result['status']=='submitted' ){

        // is enabled
        var enabled = !isBountyOwner(result);
        var interestEntry = {
            href: is_interested ? '/uninterested' : '/interested',
            text: is_interested ? 'Stop Work' : 'Start Work',
            parent: 'right_actions',
            color: enabled ? 'darkBlue' : 'darkGrey',
            extraClass: enabled ? '' : 'disabled',
            title: enabled ? 'Start Work in an issue to let the issue funder know that youre starting work on this issue.' : 'Can only be performed if you are not the funder.',
        }
        actions.push(interestEntry);

    }

    // is enabled
    var enabled = !isBountyOwner(result);
    var entry = {
        href: '/funding/fulfill?source='+result['github_url'],
        text: 'Submit Work',
        parent: 'right_actions',
        color: enabled ? 'darkBlue' : 'darkGrey',
        extraClass: enabled ? '' : 'disabled',
        title: enabled ? 'Use Submit Work when you FINISH work on a bounty. ' : 'Can only be performed if you are not the funder.',
    }
    actions.push(entry);

    var is_date_expired = (new Date(result['now']) > new Date(result['expires_date']));
    var is_status_expired = result['status']=='expired';
    var is_status_done = result['status']=='done';
    if(!is_status_done && !is_status_expired){
        var enabled = isBountyOwner(result);
        var entry = {
            href: '/funding/kill?source='+result['github_url'],
            text: 'Kill Bounty',
            parent: 'right_actions',
            color: enabled ? 'darkBlue' : 'darkGrey',
            extraClass: enabled ? '' : 'disabled',
            title: enabled ? '' : 'Can only be performed if you are the funder.',
        }
        actions.push(entry);
    }

    render_actions(actions);

    });
}

var render_actions = function(actions){
    for(var l=0; l< actions.length; l++){
        var target = actions[l]['parent'];
        var tmpl = $.templates("#action");
        var html = tmpl.render(actions[l]);
        $("#"+target).append(html);
    };
}

var pull_bounty_from_api = function(){
    var uri = '/actions/api/v0.1/bounties/?github_url=' + document.issueURL;
    $.get(uri, function(results){
        results = sanitizeAPIResults(results);
        var nonefound = true;
        // potentially make this a lot faster by only pulling the specific issue required
        for(var i = 0; i<results.length; i++){
            var result = results[i];
            // if the result from the database matches the one in question.
            if(normalizeURL(result['github_url']) == normalizeURL(document.issueURL)){
                nonefound = false;

                build_detail_page(result);

                do_actions(result);

                render_fulfillments(result);

                //cleanup
                document.result = result;
                return;
            }
        }
        if (nonefound) {
            $("#primary_view").css('display','none');
            // is there a pending issue or not?
            $(".nonefound").css('display','block');
        }
    }).fail(function(){
        _alert('got an error. please try again, or contact support@gitcoin.co');
            $("#primary_view").css('display','none');
    }).always(function(){
        $('.loading').css('display', 'none');
    });
}

var render_fulfillments = function(result){
    // Add submitter list and accept buttons
    if(result['status']=='submitted' ){
        var enabled = isBountyOwner(result);

        fulfillers = [];
        var submissions = result.fulfillments;
        $.each(submissions, function (index, value) {
            var acceptButton = {
                href: '/funding/process?source='+result['github_url']+"&id="+value.fulfillment_id,
                text: 'Accept Submission',
                color: enabled ? 'darkBlue' : 'darkGrey',
                extraClass: enabled ? '' : 'disabled',
                title: enabled ? 'This will payout the bounty to the submitter.' : 'Can only be performed if you are the funder.',
            };

            var submission = {
                'fulfiller': value,
                'button': acceptButton,
            };
            submission['fulfiller']['created_on'] = timeDifference(new Date(), new Date(submission['fulfiller']['created_on']));
            var submitter_tmpl = $.templates("#submission");
            var submitter_html = submitter_tmpl.render(submission);

            $("#submission_list").append(submitter_html);
        });
    } else if (result['status']=='done') {
        fulfillers = [];
        var submissions = result.fulfillments;
        $.each(submissions, function (index, value) {
            var accepted = value.accepted;
            var acceptedButton = {
                href: '',
                text: accepted ? 'Accepted' : 'Not Accepted',
                color: accepted ? 'darkBlue' : 'darkGrey',
                extraClass: accepted ? '' : 'disabled',
                title: accepted ? 'This submisson has been accepted.' : 'This submission has not been accepted.',
            };

            var submission = {
                'fulfiller': value,
                'button': acceptedButton,
            };

            var submitter_tmpl = $.templates("#submission");
            var submitter_html = submitter_tmpl.render(submission);

            $("#submission_list").append(submitter_html);
        });
    } else {
        submitter_html = "No one has submitted work yet.";
        $("#submission_list").html(submitter_html);
    }
}

var main = function(){
    setTimeout(function(){
        //setup
        attach_work_actions();

        // pull issue URL
        document.issueURL = getParam('url');
        $("#submitsolicitation a").attr('href','/funding/new/?source=' + document.issueURL);

        // if theres a pending submission for this issue, show the warning message
        // if not, pull the data from the API
        if(localStorage[document.issueURL]){
            //update from web3
            document.pendingIssueMetadata = JSON.parse(localStorage[document.issueURL]);
            var txid = document.pendingIssueMetadata['txid'];
            showWarningMessage(txid);
            wait_for_tx_to_mine_and_then_ping_server();
        } else {
            pull_bounty_from_api();
        }

    }, 100);
};


window.addEventListener('load', function() {
    main();
});
