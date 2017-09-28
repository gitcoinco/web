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
        return [ key, "<a target=new href=https://github.com/"+val+">@"+val+"</a>"];
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
    'title',
    'web3_created',
    'status',
    'github_url',
    'value_in_token',
    'value_in_eth',
    'value_in_usdt',
    'bounty_owner_address',
    'bounty_owner_email',
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
    'title': 'Bounty Info',
    'bounty_owner_address': 'Bounty Submitter',
    'claimeee_address': 'Claimee',
    'experience_level': 'Meta',
}
var display_name = {
    'title': "title",
    'github_url': "Issue URL",
    'value_in_token': "Amount",
    'bounty_owner_address': "Address",
    'bounty_owner_email': "Email",
    'bounty_owner_github_username': "GitHub Profile",
    'claimeee_address': "Address",
    'claimee_github_username': "GitHub Profile",
    'claimee_email': "Email",
    'experience_level': "Experience Level",
    'project_length': "Project Length",
    'bounty_type': "Bounty Type",
    'expires_date': "Expires",
    'value_in_usdt' : "Amount (USDT)",
};
var callbacks = {
    'github_url': link_ize,
    'value_in_token': function(key, val, result){
        return [ 'amount', Math.round((parseInt(val) / 10**document.decimals) * 1000) / 1000 + " " + result['token_name']];
    },
    'claimeee_address': address_ize,
    'bounty_owner_address': address_ize,
    'bounty_owner_email': email_ize,
    'claimee_email': email_ize,
    'experience_level': unknown_if_empty,
    'project_length': unknown_if_empty,
    'bounty_type': unknown_if_empty,
    'claimee_github_username': github_ize,
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
        return [ "Amount (USDT)" , val];
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
                            console.log(error);
                        } else {
                            result[0] = result[0].toNumber();
                            result[7] = result[7].toNumber();
                            result[9] = result[9].toNumber();
                            was_success = result[0] > 0;
                            if(was_success){
                                console.log('success syncing with web3');
                                sync_web3(issueURL, result, changes_synced_callback);
                            } else {
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
            var msg = `<br>This bounty has recently been updated and while the blockchain syncs it has `+pendingchanges+`.  
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
                    $(".result_container").css('display','flex','important');
                    nonefound= false;

                    //setup
                    var decimals = 18;
                    var related_token_details = tokenAddressToDetails(result['token_address'])
                    if(related_token_details && related_token_details.decimals){
                        decimals = related_token_details.decimals;
                    }
                    document.decimals = decimals;

                    // title
                    result['title'] = result['title'] ? result['title'] : result['github_url'];
                    $('.title').html("Bounty Details: " + result['title']);

                    //nav
                    var status = result['status'];
                    if(status == 'submitted'){
                       $('.bounty_nav li.submit').addClass('active');
                    } else if(status == 'fulfilled'){
                       $('.bounty_nav li.accept').addClass('active');
                    } else if(status == 'claimed'){
                       $('.bounty_nav li.fulfill').addClass('active');
                    } else {
                    }

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
                            key = _result[0];
                            val = _result[1];
                        }
                        if(display_name[key]){
                            key = display_name[key];
                        }
                        if(key){
                            var entry = {
                                'head': head,
                                'key': key,
                                'val': val,
                            }
                            var tmpl = $.templates("#result");
                            var html = tmpl.render(entry);
                            $(".result_container").append(html);
                        }
                    }

                    //actions
                    var entry = {
                        href: result['github_url'],
                        text: 'View on Github',
                    }
                    var actions = [entry];
                    if(status=='submitted'){
                        var entry = {
                            href: '/bounty/claim?source='+result['github_url'],
                            text: 'Claim Issue',
                        }
                        actions.push(entry);
                    }
                    if(status=='claimed'){
                        var entry = {
                            href: '/bounty/process?source='+result['github_url'],
                            text: 'Accept/Reject Issue',
                        }
                        actions.push(entry);
                    }
                    if(is_on_watch_list(result['github_url'])){
                        var entry = {
                            href: '/unwatch',
                            text: 'Unwatch',
                        }
                        actions.push(entry);
                    } else {
                        var entry = {
                            href: '/watch',
                            text: 'Watch',
                        }
                        actions.push(entry);
                    }

                    for(var l=0; l< actions.length; l++){
                        var tmpl = $.templates("#action");
                        var html = tmpl.render(actions[l]);
                        $("#actions").append(html);
                    }
                    
                    //cleanup
                    document.result = result;
                    pendingChangesWarning(issueURL, result['modified_on'], result['now']);
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