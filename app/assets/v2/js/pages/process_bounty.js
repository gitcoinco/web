window.onload = function(){
    //a little time for web3 injection
    setTimeout(function(){
        var account = web3.eth.accounts[0];

        if(getParam('source')){
            $('input[name=issueURL]').val(getParam('source'));
        }
        if (typeof localStorage['acceptTOS'] !='undefined' && localStorage['acceptTOS']){
            $('input[name=terms]').attr('checked','checked');
        }

        var estimateGas = function(issueURL, method, success_callback, failure_calllback, final_callback){
            var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
            $("#gasLimit").addClass('loading');
            method.estimateGas(
                issueURL, 
                function(errors,result){
                    $("#gasLimit").removeClass('loading');
                    console.log(errors,result);
                    var is_issue_taken = typeof result == 'undefined' || result > 209568;
                    if(errors || is_issue_taken){
                        failure_calllback(errors);
                        return;
                    }
                    var gas = Math.round(result * gasMultiplier);
                    var gasLimit = Math.round(gas * gasLimitMultiplier);
                    success_callback(gas, gasLimit, final_callback);
            });
        };
        //updates recommended metamask settings
        var updateInlineGasEstimate = function(){
            var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
            var issueURL = $('input[name=issueURL]').val();
            var success_callback = function(gas, gasLimit, _){
                $("#gasLimit").val(gas);
                update_metamask_conf_time_and_cost_estimate();
            };
            var failure_callback = function(){
                $("#gasLimit").val('Unknown');
                update_metamask_conf_time_and_cost_estimate();
            };
            var final_callback = function(){};
            //estimateGas(issueURL, bounty.approveBountyClaim, success_callback, failure_callback, final_callback);
            success_callback(50531*16,50531*16,'');
        };
        setTimeout(function(){
            updateInlineGasEstimate();
        },100);
        $('input').change(updateInlineGasEstimate);
        $('#gasPrice').keyup(update_metamask_conf_time_and_cost_estimate);

        var bountyDetails = []

        $('.submitBounty').click(function(e){
            mixpanel.track("Process Bounty Clicked", {});
            e.preventDefault();
            var whatAction = $(this).html().trim()
            var issueURL = $('input[name=issueURL]').val();

            var isError = false;
            if($('#terms:checked').length == 0){
                _alert({ message: "Please accept the terms of service." });
                isError = true;
            } else {
                localStorage['acceptTOS'] = true;
            }
            if(issueURL == ''){
                _alert({ message: "Please enter a issue URL." });
                isError = true;
            }
            if(isError){
                return;
            }

            var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
            loading_button($(this));

            var apiCallback = function(results, status){
                if(status != "success"){
                    mixpanel.track("Process Bounty Error", {step: 'callback', error: error});
                    _alert({ message: "Could not get bounty details" });
                    console.error(error);
                    unloading_button($('.submitBounty'));
                    return;
                } else {
                    results = sanitizeAPIResults(results);
                    result = results[0];

                    var bountyAmount = parseInt(result['value_in_token'], 10); 
                    var fromAddress = result['bounty_owner_address'];
                    var claimeeAddress = result['claimeee_address'];
                    var open = result['is_open'];
                    var initialized = true;
                    var bountyId = result['standard_bounties_id'];

                    // bountyDetails = [bountyAmount, result[1], result[2], result[3]];

                    var errormsg = undefined;
                    if(bountyAmount == 0 || open == false || initialized == false){
                        errormsg = "No active funding found at this address.  Are you sure this is an active funded issue?";
                    } else if(claimeeAddress == '0x0000000000000000000000000000000000000000'){
                        errormsg = "No claimee found for this bounty.";
                    } else if(fromAddress != web3.eth.coinbase){
                        errormsg = "You can only process a funded issue if you submitted it initially.";
                    }

                    if(errormsg){
                        _alert({ message: errormsg });
                        unloading_button($('.submitBounty'));
                        return;
                    }

                    var _callback = function(error, result){
                        var next = function(){
                            localStorage['txid'] = result;
                            updates = {
                                is_open: false,  // Close out the bounty in the database
                                idx_status: 'accepted',
                            }
                            sync_web3(issueURL, JSON.stringify(updates));
                            localStorage[issueURL] = timestamp();
                            add_to_watch_list(issueURL);
                            _alert({ message: "Submitted transaction to web3." }, 'info');
                            setTimeout(function(){
                                mixpanel.track("Process Bounty Success", {});
                                document.location.href= "/funding/details?url="+issueURL;
                            },1000);

                        };
                        if(error){
                            mixpanel.track("Process Bounty Error", {step: '_callback', error: error});
                            _alert({ message: "There was an error" });
                            console.error(error);
                            unloading_button($('.submitBounty'));
                        } else {
                            next();
                        }
                    };

                    // Standard Bounties can have multiple fulfillments by multiple people.
                    // Gitcoin does not support this yet, it only allows one person to fulfill.
                    // Just in case multilple fulfillments end up on the bounty, we will take 
                    // the latest one, which will match up with what the database has.
                    bounty.getNumFulfillments(bountyId, function (error, result) {
                        var fulfillmentId = result - 1;
                        bounty.acceptFulfillment(bountyId, fulfillmentId, _callback);
                    });

                    // var method = bounty.approveBountyClaim;
                    // if(whatAction != 'Accept'){
                    //     method = bounty.rejectBountyClaim;
                    // }
                    var failure_calllback = function(errors){
                        mixpanel.track("Process Bounty Error", {step: 'estimateGas', error: errors});
                        _alert({ message: "There was an error" });
                        unloading_button($('.submitBounty'));

                    }
                    var success_callback = function(gas, gasLimit){
                        var params = {from :account, 
                                gas:web3.toHex(gas), 
                                gasLimit: web3.toHex(gasLimit), 
                                gasPrice:web3.toHex($("#gasPrice").val() * 10**9), 
                            };
                        method.sendTransaction(issueURL, 
                            params, 
                            _callback);
                    };
                    // estimateGas(issueURL, method, success_callback, failure_calllback, _callback);
                }
            };
            // Get bountyId from the database
            var uri = '/api/v0.1/bounties?github_url='+issueURL;
            $.get(uri, apiCallback); 
            e.preventDefault();
        });
    },100);

};
