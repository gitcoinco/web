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
var github_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a target=new href=https://github.com/"+val+">@"+val.replace('@','')+"</a>"];
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
    'web3_created',
    'status',
    'bounty_owner_address',
    'bounty_owner_email',
    'issue_description',
    'bounty_owner_github_username',
    'claimeee_address',
    'claimee_github_username',
    'claimee_email',
    'experience_level',
    'project_length',
    'bounty_type',
    'expires_date',
]
var heads = {
    'avatar_url': 'Issue',
    'value_in_token': 'Issue Funding Info',
    'bounty_owner_address': 'Funder',
    'claimeee_address': 'Claimee',
    'experience_level': 'Meta',
}
var callbacks = {
    'github_url': link_ize,
    'value_in_token': function(key, val, result){
        return [ 'amount', Math.round((parseInt(val) / 10**document.decimals) * 1000) / 1000 + " " + result['token_name']];
    },
    'avatar_url': function(key, val, result){
        return [ 'avatar', '<a href="/profile/'+result['org_name']+'"><img class=avatar src="'+val+'"></a>'];
    },
    'status': function(key, val, result){
        var ui_status = val;
        if(ui_status=='open'){
            ui_status = '<span style="color: #47913e;">active</span>';
        }
        if(ui_status=='claimed'){
            ui_status = '<span style="color: #3e00ff;">claimed</span>';
        }
        return [ 'status', ui_status];
    },
    'issue_description': function(key, val, result){
        var ui_body = val;
        var allowed_tags = ['br', 'li', 'em', 'ol', 'ul', 'p', 'td', 'a', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code'];
        var open_close = ['', '/'];
        var replace_tags = {
            'h1': 'h5',
            'h2': 'h5',
            'h3': 'h5',
            'h4': 'h5',
        }

        for(var i=0; i<allowed_tags.length;i++){
            var tag = allowed_tags[i];
            for(var k=0; k<open_close.length;k++){
                var oc = open_close[k];
                var replace_tag = '&lt;'+ oc + tag +'.*&gt;';
                var with_tag = '<'+ oc + tag +'>';
                var re = new RegExp(replace_tag, 'g');
                ui_body = ui_body.replace(re, with_tag);
                var re = new RegExp(replace_tag.toUpperCase(), 'g');
                ui_body = ui_body.replace(re, with_tag);
            }
        }
        for(var key in replace_tags){
            for(var k=0; k<open_close.length;k++){
                var oc = open_close[k];
                var replace = key;
                var _with = replace_tags[key];
                var replace_tag = '<'+ oc + replace +'>';
                var with_tag = '<'+ oc + _with +'>';
                var re = new RegExp(replace_tag, 'g');
                ui_body = ui_body.replace(re, with_tag);
            }
        }

        var max_len = 1000
        if(ui_body.length > max_len){
            ui_body = ui_body.substring(0, max_len) + '... <a target=new href="'+result['github_url']+'">See More</a> '
        }
        return [ 'issue_description', ui_body];
    },
    'claimeee_address': address_ize,
    'bounty_owner_address': address_ize,
    'bounty_owner_email': email_ize,
    'claimee_email': email_ize,
    'experience_level': unknown_if_empty,
    'project_length': unknown_if_empty,
    'bounty_type': unknown_if_empty,
    'claimee_email': function(key, val, result){
        if(!_truthy(result['claimeee_address'])){
            $("#claimee").addClass('hidden');
        }
        return address_ize(key, val, result);
    },
    'bounty_owner_github_username': github_ize,
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
    'web3_created': function(key, val, result){
        return [ "updated" , timeDifference(new Date(result['now']), new Date(result['created_on']))];
    },
    'expires_date': function(key, val, result){
        expires_date = new Date(val);
        now = new Date(result['now']);
        var response = timeDifference(now, expires_date);
        return [ "expires" , response];
    },
    
}


var pendingChangesWarning = function(issueURL, last_modified_time_remote, now){
        //setup callbacks
        var changes_synced_callback = function(){
            document.location.href = document.location.href;
            //check_for_bounty_changed_updates_REST();
        };
        var check_for_bounty_changed_updates_REST = function(){
            var uri = '/api/v0.1/bounties?github_url='+issueURL;
             $.get(uri, function(results){
                results = sanitizeAPIResults(results);
                var result = results[0];
                // if remote entry has been modified, refresh the page.  if not, try again
                if(typeof result == 'undefined' || result['modified_on'] == last_modified_time_remote){
                    setTimeout(check_for_bounty_changed_updates_REST,2000);
                } else {
                    changes_synced_callback();
                }
             });
        };
        var check_for_bounty_changed_updates_web3 = function(){
            callFunctionWhenTransactionMined(localStorage['txid'],function(){
                var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
                setTimeout(function(){
                    bounty.bountydetails.call(issueURL, function(error, result){
                        if(error){
                            setTimeout(check_for_bounty_changed_updates_web3, 1000);
                            console.error(error);
                        } else {
                            result[0] = result[0].toNumber();
                            result[7] = result[7].toNumber();
                            result[9] = result[9].toNumber();
                            was_success = result[0] > 0;
                            if(was_success){
                                console.log('success syncing with web3');
                                sync_web3(issueURL, result, changes_synced_callback);
                            } else {
                                console.error(result);
                                var link_url = etherscan_tx_url(localStorage['txid']);
                                _alert("<a target=new href='"+link_url+"'>There was an error executing the transaction.</a>  Please <a href='#' onclick='window.history.back();'>try again</a> with a higher gas value.  ")
                            }
                        }
                    });
                },1000);
            });
        };

        var showWarningMessage = function(){
            var pendingchanges = 'pending changes';
            var this_transaction = 'this transaction';
            var title = '';
            if(typeof localStorage['txid'] != 'undefined' && localStorage['txid'].indexOf('0x') != -1){
                var link_url = etherscan_tx_url(localStorage['txid']);
                pendingchanges = "<a target=new href='"+link_url+"'>"+pendingchanges+"</a>"
                this_transaction = "<a target=new href='"+link_url+"'>"+this_transaction+"</a>"
                title = "Your transaction has been posted to web3.";
            }
            var msg = `<br>This funded issue has recently been updated and while the blockchain syncs it has `+pendingchanges+`.  
            Please wait a minute or two for web3 to sync `+this_transaction+`.
            <br>(You can close the browser tab.  If not, this page will automatically refresh as soon as web3 is updated.)`
            _alert({ title: title, message: msg},'info');
        }


    var should_display_warning = false;
    if(localStorage[issueURL]){
        //local warning
        var local_delta = parseInt(timestamp() - localStorage[issueURL]);
        var is_changing_local_recent = local_delta < (60 * 60); // less than one hour

        //remote warning 
        var remote_delta = (new Date(now) - new Date(last_modified_time_remote)) / 1000;
        var is_changing_remote_recent = remote_delta < (60 * 60); // less than one minute

        should_display_warning = !last_modified_time_remote || ((is_changing_local_recent) && (remote_delta > local_delta));
        if(should_display_warning){

            showWarningMessage();
            showLoading();
            check_for_bounty_changed_updates_web3();
        }
    }
    return should_display_warning;
};


window.addEventListener('load', function() {
    setTimeout(function(){
        var issueURL = getParam('url');
        var uri = '/api/v0.1/bounties?';
        $.get(uri, function(results){
            results = sanitizeAPIResults(results);
            var nonefound = true;
            for(var i = 0; i<results.length; i++){
                var result = results[i];
                if(normalizeURL(result['github_url']) == normalizeURL(issueURL)){
                    $("#bounty_details").css('display','flex');
                    nonefound = false;

                    //setup
                    var decimals = 18;
                    var related_token_details = tokenAddressToDetails(result['token_address'])
                    if(related_token_details && related_token_details.decimals){
                        decimals = related_token_details.decimals;
                    }
                    document.decimals = decimals;

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

                    //actions
                    var actions = [];
                    if(result['github_url'].substring(0,4) == 'http'){

                        var github_url = result['github_url'];
                        // hack to get around the renamed repo for piper's work.  can't change the data layer since blockchain is immutable
                        github_url = github_url.replace('pipermerriam/web3.py','ethereum/web3.py');

                        var entry = {
                            href: github_url,
                            text: 'View on Github',
                            target: 'new',
                            parent: 'right_actions',
                            color: 'darkGrey'
                        }
                    }
                    actions.push(entry);
                    if(result['status']=='open'){
                        var entry = {
                            href: '/funding/claim?source='+result['github_url'],
                            text: 'Claim Issue',
                            parent: 'right_actions',
                            color: 'darkBlue'
                        }
                        actions.push(entry);
                    }
                    if(result['status']=='expired' && web3 && web3.eth.coinbase == result['bounty_owner_address'] ){
                        var entry = {
                            href: '/funding/clawback?source='+result['github_url'],
                            text: 'Clawback Expired Funds',
                            parent: 'right_actions',
                            color: 'darkBlue'
                        }
                        actions.push(entry);
                    }
                    if(result['status']=='claimed'){
                        var entry = {
                            href: '/funding/process?source='+result['github_url'],
                            text: 'Accept/Reject Issue',
                            parent: 'right_actions',
                            color: 'darkBlue'
                        }
                        actions.push(entry);
                    }
                    if(is_on_watch_list(result['github_url'])){
                        var entry = {
                            href: '/unwatch',
                            text: 'Unwatch',
                            parent: 'left_actions',
                            color: 'darkGrey'
                        }
                        actions.push(entry);
                    } else {
                        var entry = {
                            href: '/watch',
                            text: 'Watch',
                            parent: 'left_actions',
                            color: 'darkGrey'
                        }
                        actions.push(entry);
                    }

                    for(var l=0; l< actions.length; l++){
                        var target = actions[l]['parent'];
                        var tmpl = $.templates("#action");
                        var html = tmpl.render(actions[l]);
                        $("#"+target).append(html);
                    }
                    
                    //cleanup
                    document.result = result;
                    pendingChangesWarning(issueURL, result['created_on'], result['now']);
                    add_to_watch_list(result['github_url']);
                    return;
                }
            }
            if(nonefound){
                $(".nonefound").css('display','block');
                $("#primary_view").css('display','none');
                pendingChangesWarning(issueURL);
            }
        }).fail(function(){
            _alert('got an error. please try again, or contact support@gitcoin.co');
                $("#primary_view").css('display','none');
        }).always(function(){
            $('.loading').css('display', 'none');
        });        

    },100);
});


$(document).ready(function(){
    $("body").delegate('a[href="/watch"], a[href="/unwatch"]', 'click', function(e){
        e.preventDefault();
        if($(this).attr('href') == '/watch'){
            $(this).attr('href','/unwatch');
            $(this).find('span').text('Unwatch');
            add_to_watch_list(document.result['github_url']);
        } else {
            $(this).attr('href','/watch');
            $(this).find('span').text('Watch');
            remove_from_watch_list(document.result['github_url']);
        }
    });
});