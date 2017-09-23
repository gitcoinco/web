
window.addEventListener('load', function() {
    setTimeout(function(){
        //add tokens to the submission form
        var tokenAddress = localStorage['tokenAddress'];
        if(!tokenAddress){
            tokenAddress='0x0000000000000000000000000000000000000000';
        }
        var _tokens = tokens(document.web3network);
        for(var i=0;i<_tokens.length;i++){
            var token = _tokens[i];
            var select = {
                value: token['addr'],
                text: token['name'],
            };
            if(token['addr']==tokenAddress){
                select['selected']='selected';
            }
            $("select[name=deonomination]").append($('<option>', select))
        }
        //if web3, set the values of some form variables
        if (typeof localStorage['amount'] !='undefined'){
            $('input[name=amount]').val(localStorage['amount']);
        }
        if (typeof localStorage['githubUsername'] !='undefined'){
            $('input[name=githubUsername]').val(localStorage['githubUsername']);
        }
        if (typeof localStorage['notificationEmail'] !='undefined'){
            $('input[name=notificationEmail]').val(localStorage['notificationEmail']);
        }

    },100);

});


$(document).ready(function(){

    //fetch issue URL related info
    $("input[name=issueURL]").blur(retrieveTitle);
    $("input[name=issueURL]").blur(retrieveKeywords);

    if($("input[name=issueURL]").val()!=''){
        retrieveTitle();
        retrieveKeywords();
    }
    $('input[name=issueURL]').focus();

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
    
    //submit bounty button click
    $('#submitBounty').click(function(e){
        //setup
        e.preventDefault();
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
        }
        if(issueURL == ''){
            _alert({ message: "Please enter an issue URL." });
            isError = true;
        }
        if(amount == ''){
            _alert({ message: "Please enter an amount." });
            isError = true;
        }
        if(isError){
            return;
        }
        $(this).attr('disabled','disabled');

        //save off local state for later
        localStorage['amount'] = amount;
        localStorage['notificationEmail'] = notificationEmail;
        localStorage['githubUsername'] = githubUsername;
        localStorage['tokenAddress'] = tokenAddress;

        //setup web3
        var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
        var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
        var account = web3.eth.coinbase;
        amount = amount * decimalDivisor;
        const gasPrice = 1000000000 * 16; //16 gwei
        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

        //setup callback functions for web3 calls
        var callback2 = function(error, result){
            if(error){
                console.log("two", error);
                    _alert({ message: "There was an error.  Please try again or conact support." });
                $('#submitBounty').removeAttr('disabled');
            } else {
                callFunctionWhenTransactionMined(result,function(){
                    sync_web3(issueURL);
                    localStorage[issueURL] = timestamp();
                    add_to_watch_list(issueURL);
                    document.location.href= "/bounty/details?url="+issueURL;
                    _alert({ message: "Transaction complete." }, 'info');
                });

            }
        }
        var sendPostBounty = function(){
            var value = 0;
            if(isETH){
                value = amount;
            }
            bounty.postBounty.estimateGas(issueURL, 
                amount, 
                tokenAddress, 
                expirationTimeDelta, 
                JSON.stringify(metadata),
                {from :account, value:value},
                function(errors, result){
                    var gas = result + 10;
                    var gasLimit = gas * 2;
                    bounty.postBounty.sendTransaction(issueURL, 
                        amount, 
                        tokenAddress, 
                        expirationTimeDelta, 
                        JSON.stringify(metadata),
                        {from :account, 
                            gas:gas, 
                            gasLimit: gasLimit, 
                            gasPrice:gasPrice, 
                            value:value},
                        callback2);

                });
        };
        var callback = function(error, result){
            var next = function(){
                callFunctionWhenTransactionMined(result,function(){
                    _alert({ message: "Transaction sent." }, 'info');
                    _alert({ title: "Next", message: "Submit the bounty to the bounty contract."  }, 'info');
                    sendPostBounty();
                });
            };
            if(error){
                var isApprovalAlreadyGranted = error.toString().indexOf('invalid opcode') != -1;
                if (isApprovalAlreadyGranted){
                    next();
                } else {
                    _alert({ message: "There was an error.  Please try again or conact support." });
                    $('#submitBounty').removeAttr('disabled');
                }
            } else {
                next();
            }
        };
        var sendERC20Approve = function(){
            token_contract.approve.estimateGas(bounty_address()
                ,amount, 
                function(errors,result){
                    var gas = result + 10;
                    var gasLimit = gas * 2;
                    token_contract.approve.sendTransaction(bounty_address()
                        ,amount, 
                        {from :account, 
                            gas:gas, 
                            gasLimit: gasLimit, 
                            gasPrice:gasPrice},
                        callback);
                });
        };
        // actually send the transactions to web3
        setTimeout(function(){
            bounty.bountydetails.call(issueURL, function(error, result){
                if(error){
                    console.log(error);
                    _alert({ message: "There was an error.  Please try again or conact support." });
                    return;
                }
                var isOpenAlready = result[4];
                if(isOpenAlready){
                    _alert("There is already an open bounty on this issue.  Please try again with another issue.");
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