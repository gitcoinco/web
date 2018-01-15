load_tokens();
var setUsdAmount= function (event) {
    var amount  = $('input[name=amount]').val();
    var denomination  = $('#token option:selected').text();
    var estimate = getUSDEstimate(amount, denomination, function(estimate){
        $('#usd_amount').html(estimate);
    });
};

$(document).ready(function(){

    if(getParam('source')){
        $('input[name=issueURL]').val(getParam('source'));
    }
    if(localStorage['expirationTimeDelta']){
        $('select[name=expirationTimeDelta] option').prop('selected', false);
        $('select[name=expirationTimeDelta] option[value=\''+localStorage['expirationTimeDelta']+'\']').prop('selected', true);
    }
    if(localStorage['experienceLevel']){
        $('select[name=experienceLevel] option:contains('+localStorage['experienceLevel']+')').prop('selected', true);
    }
    if(localStorage['projectLength']){
        $('select[name=projectLength] option:contains('+localStorage['projectLength']+')').prop('selected', true);
    }
    if(localStorage['bountyType']){
        $('select[name=bountyType] option:contains('+localStorage['bountyType']+')').prop('selected', true);
    }
    if(localStorage['issueURL']){
        $('input[name=issueURL]').val(localStorage['issueURL']);
    }
    //fetch issue URL related info
    $("input[name=amount]").keyup(setUsdAmount);
    $("input[name=amount]").blur(setUsdAmount);
    $("select[name=deonomination]").change(setUsdAmount);
    $("input[name=issueURL]").blur(retrieveTitle);
    $("input[name=issueURL]").blur(retrieveKeywords);

    if($("input[name=issueURL]").val()!=''){
        retrieveTitle();
        retrieveKeywords();
    }
    $('input[name=issueURL]').focus();

    $('select[name=deonomination').select2();

    $('#advancedLink a').click(function(e){
        e.preventDefault();
        var target = $("#advanced_container");
        if(target.css('display') == 'none'){
            target.css('display','block');
            $(this).text('Advanced ⬆');
        } else {
            target.css('display','none');
            $(this).text('Advanced ⬇ ');
        }
    });

        var estimateGas = function(issueURL, success_callback, failure_calllback, final_callback){
                //TODO: DRY
                var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
                var githubUsername = $('input[name=githubUsername]').val();
                var issueURL = $('input[name=issueURL]').val();
                var notificationEmail = $('input[name=notificationEmail]').val();
                var amount = $('input[name=amount]').val();
                var tokenAddress = $('select[name=deonomination').val();
                var token =  (tokenAddress);
                var decimals = token['decimals'];
                var tokenName = token['name'];
                var decimalDivisor = 10**decimals;
                var expirationTimeDelta = $('select[name=expirationTimeDelta').val();
                var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
                var metadata = {
                    issueTitle : $('input[name=title').val(),
                    issueKeywords : $('input[name=keywords').val(),
                    tokenName : tokenName,
                    githubUsername : githubUsername,
                    notificationEmail : notificationEmail,
                    experienceLevel : $('select[name=experienceLevel').val(),
                    projectLength : $('select[name=projectLength').val(),
                    bountyType : $('select[name=bountyType').val(),
                }
                var value = 0;
                if(isETH){
                    value = amount;
                }
                $("#gasLimit").addClass('loading');
                bounty.postBounty.estimateGas(issueURL, 
                    amount, 
                    tokenAddress, 
                    expirationTimeDelta, 
                    JSON.stringify(metadata),
                    {from :web3.eth.coinbase, value:value},
                    function(errors,result){
                        $("#gasLimit").removeClass('loading');
                        var is_issue_taken = typeof result == 'undefined' || result > 12976605;
                        if(errors || is_issue_taken){
                            failure_calllback(errors)
                            return;
                        }
                        var gas = Math.round(result * gasMultiplier);
                        var gasLimit = Math.round(gas * gasLimitMultiplier);
                        // for some reason web3 was estimating 6699496 as the gas for standardtoken transfers
                        if((gas > max_gas_for_erc20_bounty_post) && !isETH){
                            gas = Math.round(max_gas_for_erc20_bounty_post * gasMultiplier);
                            gasLimit = Math.round(gas * gasMultiplier);
                        }

                        success_callback(gas, gasLimit, final_callback);
                });    
        }
        //updates recommended metamask settings
        var updateInlineGasEstimate = function(){
            var success_callback = function(gas, gasLimit, _){
                $("#gasLimit").val(parseInt(gas/16.1));
                update_metamask_conf_time_and_cost_estimate();
            };
            var failure_callback = function(errors){
                $("#gasLimit").val('Unknown');
                update_metamask_conf_time_and_cost_estimate();
            };
            var final_callback = function(){};
            //estimateGas(issueURL, success_callback, failure_callback, final_callback);
            success_callback(682443*16,682443*16,'');
        };
        setTimeout(function(){
            updateInlineGasEstimate();
        },500);
        $('input').change(updateInlineGasEstimate);
        $('#gasPrice').keyup(update_metamask_conf_time_and_cost_estimate);



    
    //submit bounty button click
    $('#submitBounty').click(function(e){
        mixpanel.track("Submit New Bounty Clicked", {});

        //setup
        e.preventDefault();
        loading_button($(this));
        var githubUsername = $('input[name=githubUsername]').val();
        var issueURL = $('input[name=issueURL]').val();
        var notificationEmail = $('input[name=notificationEmail]').val();
        var amount = $('input[name=amount]').val();
        var tokenAddress = $('select[name=deonomination').val();
        var token = tokenAddressToDetails(tokenAddress);
        var decimals = token['decimals'];
        var tokenName = token['name'];
        var decimalDivisor = 10**decimals;
        var expirationTimeDelta = $('select[name=expirationTimeDelta').val();
        var metadata = {
            issueTitle : $('input[name=title').val(),
            issueKeywords : $('input[name=keywords').val(),
            tokenName : tokenName,
            githubUsername : githubUsername,
            notificationEmail : notificationEmail,
            experienceLevel : $('select[name=experienceLevel').val(),
            projectLength : $('select[name=projectLength').val(),
            bountyType : $('select[name=bountyType').val(),
        }
        
        //validation
        var isError = false;

        if($('#terms:checked').length == 0){
            _alert({ message: "Please accept the terms of service." });
            isError = true;
        } else {
            localStorage['acceptTOS'] = true;
        }
        var is_issueURL_invalid = issueURL == '' 
            || issueURL.indexOf('http') != 0 
            || issueURL.indexOf('github') == -1 
            || issueURL.indexOf('javascript:') != -1 
        ;
        if(is_issueURL_invalid){
            _alert({ message: "Please enter a valid github issue URL." });
            isError = true;
        }
        if(amount == ''){
            _alert({ message: "Please enter an amount." });
            isError = true;
        }
        if(isError){
            unloading_button($(this));
            return;
        }
        $(this).attr('disabled','disabled');

        //save off local state for later
        localStorage['issueURL'] = issueURL;
        localStorage['amount'] = amount;
        localStorage['notificationEmail'] = notificationEmail;
        localStorage['githubUsername'] = githubUsername;
        localStorage['tokenAddress'] = tokenAddress;
        localStorage['expirationTimeDelta'] = $('select[name=expirationTimeDelta').val();
        localStorage['experienceLevel'] = $('select[name=experienceLevel').val();
        localStorage['projectLength'] = $('select[name=projectLength').val();
        localStorage['bountyType'] = $('select[name=bountyType').val();


        //setup web3
        var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
        var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
        var account = web3.eth.coinbase;
        amount = amount * decimalDivisor;
        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

        //setup callback functions for web3 calls
        var post_bounty_callback = function(error, result){
            unloading_button($('#submitBounty'));
            if(error){
                mixpanel.track("New Bounty Error", {step: 'post_bounty', error: error});
                console.error("two", error);
                    _alert({ message: "There was an error.  Please try again or contact support." });
                $('#submitBounty').removeAttr('disabled');
            } else {
                sync_web3(issueURL);
                localStorage['txid'] = result;
                localStorage[issueURL] = timestamp();
                add_to_watch_list(issueURL);
                _alert({ message: "Submission sent to web3." }, 'info');
                setTimeout(function(){
                    delete localStorage['issueURL'];
                    mixpanel.track("Submit New Bounty Success", {});
                    document.location.href= "/funding/details?url="+issueURL;
                },1000);

            }
        }
        var sendPostBounty = function(){
            var value = 0;
            if(isETH){
                value = amount;
            }
            var _bounty = web3.eth.contract(bounty_abi).at(bounty_address());
            _bounty.postBounty.estimateGas(issueURL, 
                amount, 
                tokenAddress, 
                expirationTimeDelta, 
                JSON.stringify(metadata),
                {from :account, value:value},
                function(errors, result){
                    mixpanel.track("New Bounty Error", {step: 'post_boutny', error: errors});
                    var gas = Math.round(result * gasMultiplier);
                    var gasLimit = Math.round(gas * gasLimitMultiplier);

                    // for some reason web3 was estimating 6699496 as the gas for standardtoken transfers
                    if((gas > max_gas_for_erc20_bounty_post) && !isETH){
                        gas = Math.round(max_gas_for_erc20_bounty_post * gasMultiplier);
                        gasLimit = Math.round(gas * gasMultiplier);
                    }
                    _bounty.postBounty.sendTransaction(issueURL, 
                        amount, 
                        tokenAddress, 
                        expirationTimeDelta, 
                        JSON.stringify(metadata),
                        {from :account, 
                            gas:web3.toHex(gas), 
                            gasLimit: web3.toHex(gasLimit), 
                            gasPrice:web3.toHex($("#gasPrice").val() * 10**9), 
                            value:value},
                        post_bounty_callback);

                });
        };
        var erc20_approve_callback = function(error, result){
            var next = function(){
                callFunctionWhenTransactionMined(result,function(){
                    _alert({ title: "Transaction #2", message: "Thanks for approving the token transfer.  Now, submit the funded issue to the contract."  }, 'info');
                    sendPostBounty();
                });
            };
            if(error){
                mixpanel.track("New Bounty Error", {step: 'erc20', error: error});
                console.error(error);
                unloading_button($('#submitBounty'));
                var isApprovalAlreadyGranted = error.toString().indexOf('invalid opcode') != -1;
                if (isApprovalAlreadyGranted){
                    next();
                } else {
                    _alert({ message: "There was an error.  Please try again or contact support." });
                    $('#submitBounty').removeAttr('disabled');
                }
            } else {
                var url = etherscan_tx_url(result);
                var msg = "We've just submited the <a href="+url+" target=new>first transaction to the blockchain</a>.  Hang tight for a few seconds (can sometimes take up to a minute depending upon gas settings & network state) while it confirms.";
                _alert({ title: "Transaction #1 Submitted", message: msg  }, 'info');
                next();
            }
        };
        var sendERC20Approve = function(){
            token_contract.approve.estimateGas(bounty_address()
                ,amount, 
                function(errors,result){
                    mixpanel.track("New Bounty Error", {step: 'erc20', error: errors});
                    var gas = Math.round(erc20_approve_gas * gasMultiplier);
                    var gasLimit = Math.round(gas * gasLimitMultiplier);
                    token_contract.approve.sendTransaction(bounty_address()
                        ,amount, 
                        {from :account, 
                            gas:web3.toHex(gas), 
                            gasLimit: web3.toHex(gasLimit), 
                            gasPrice:web3.toHex($("#gasPrice").val() * 10**9), 
                        },
                        erc20_approve_callback);
                });
        };
        // actually send the transactions to web3
        setTimeout(function(){
            bounty.bountydetails.call(issueURL, function(error, result){
                if(error){
                    console.error(error);
                    mixpanel.track("New Bounty Error", {step: 'details', error: error});
                    _alert({ message: "There was an error.  Please try again or contact support." });
                    unloading_button($('#submitBounty'));
                    return;
                }
                var isOpenAlready = result[4];
                if(isOpenAlready){
                    _alert("There is already an open funding on this issue.  Please try again with another issue.");
                    unloading_button($('#submitBounty'));
                    return;
                }
                if(!isETH){
                    sendERC20Approve();
                } else {
                    sendPostBounty();
                }
            });
        },100);
        e.preventDefault();
    });

});