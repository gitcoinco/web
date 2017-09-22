
window.onload = function(){
    //a little time for web3 injection
    setTimeout(function(){
        var account = web3.eth.accounts[0];

        if (typeof localStorage['githubUsername'] !='undefined'){
            $('input[name=githubUsername]').val(localStorage['githubUsername']);
        }
        if (typeof localStorage['notificationEmail'] !='undefined'){
            $('input[name=notificationEmail]').val(localStorage['notificationEmail']);
        }


        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

        $('#submitBounty').click(function(e){
            e.preventDefault();
            var notificationEmail = $('input[name=notificationEmail]').val();
            var githubUsername = $('input[name=githubUsername]').val();
            var issueURL = $('input[name=issueURL]').val();
            var claimee_metadata = JSON.stringify({
                notificationEmail : notificationEmail,
                githubUsername : githubUsername,
            });
            localStorage['githubUsername'] = githubUsername;

            var isError = false;
            if(issueURL == ''){
                _alert({ message: "Please enter a issue URL." });
                isError = true;
            }
            if(isError){
                return;
            }

            $(this).attr('disabled','disabled');

            var _callback = function(error, result){
                if(error){
                    _alert({ message: "Could not get bounty details." });
                    console.log(error);
                    $('.submitBounty').removeAttr('disabled');
                    return;
                } else {

                    var bountyAmount = Math.round(result[0].toNumber() * web3.fromWei("1", "ether")); 
                    bountyDetails = [bountyAmount, result[1], result[2], result[3]];
                    var fromAddress = result[2];
                    var claimeeAddress = result[3];
                    var open = result[4];
                    var initialized = result[5];

                    var errormsg = undefined;
                    if(bountyAmount == 0 || open == false || initialized == false){
                        errormsg = "No active bounty found at this address.  Are you sure this is an active bounty?";
                    } 

                    if(errormsg){
                        _alert({ message: errormsg });
                        $('#submitBounty').removeAttr('disabled');
                        return;
                    }
                    const gasPrice = 1000000000 * 16; //16 gwei

                    var callback = function(error, result){
                        var next = function(){
                            callFunctionWhenTransactionMined(result,function(){
                                sync_web3(issueURL);
                                localStorage[issueURL] = timestamp();
                                add_to_watch_list(issueURL);
                                document.location.href= "/bounty/details?url="+issueURL;
                                _alert({ message: "Claim complete." },'info');
                            });

                        };
                        if(error){
                            console.log("err", error);
                            _alert({ message: "There was an error" });
                            $('#submitBounty').removeAttr('disabled');
                        } else {
                            next();
                        }
                    };

                    setTimeout(function(){
                        bounty.claimBounty.estimateGas(issueURL, 
                            claimee_metadata, 
                            {from :account}, 
                            function(errors,result){
                                var gas = result + 10;
                                var gasLimit = gas * 2;
                                bounty.claimBounty.sendTransaction(issueURL, 
                                    claimee_metadata,
                                    {from :account, gas:gas, gasLimit: gasLimit , gasPrice:defaultGasPrice}, 
                                callback);
                        });
                    },100);
                    e.preventDefault();
                }
            };
            bounty.bountydetails.call(issueURL, _callback);

        });
    },100);

};
