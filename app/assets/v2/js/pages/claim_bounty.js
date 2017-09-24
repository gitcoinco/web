
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
        if (typeof localStorage['acceptTOS'] !='undefined' && localStorage['acceptTOS']){
            $('input[name=terms]').attr('checked','checked');
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

            $(this).attr('disabled','disabled');

            var _callback = function(error, result){
                var ignore_error = false;
                if(error){
                    $('.submitBounty').removeAttr('disabled');
                    console.log(error);
                    ignore_error = String(error).indexOf('BigNumber') != -1;
                }
                var run_main = !error || ignore_error;
                if(!ignore_error){
                    _alert({ message: "Could not get bounty details." });
                }
                if(run_main){
                    if(!ignore_error){
                        var bountyAmount = result[0].toNumber();
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
                    }


                    var callback = function(error, result){
                        var next = function(){
                            localStorage['txid'] = result;
                            sync_web3(issueURL);
                            localStorage[issueURL] = timestamp();
                            add_to_watch_list(issueURL);
                            _alert({ message: "Claim submitted to web3." },'info');
                            setTimeout(function(){
                                document.location.href= "/bounty/details?url="+issueURL;
                            },1000);

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
                        console.log('est gas');
                        bounty.claimBounty.estimateGas(issueURL, 
                            claimee_metadata, 
                            {from :account}, 
                            function(errors,result){
                                console.log('got gas result');
                                var gas = result + 10;
                                // TODO: why does estimateGas seem to be :way: off for this
                                // metmask eems to think it's a 'new contract creation'
                                var gasLimit = gas * 2;
                                bounty.claimBounty.sendTransaction(issueURL, 
                                    claimee_metadata,
                                    {
                                        from : account,
                                        gas:web3.toHex(gas), 
                                        gasLimit: web3.toHex(gasLimit), 
                                        gasPrice:web3.toHex(defaultGasPrice), 
                                    }, 
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
