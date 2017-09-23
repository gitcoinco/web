const gasPrice = 1000000000 * 16; //16 gwei

window.onload = function(){
    //a little time for web3 injection
    setTimeout(function(){
        var account = web3.eth.accounts[0];
        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
        var bountyDetails = []

        $('.submitBounty').click(function(e){
            e.preventDefault();
            var whatAction = $(this).val();
            var issueURL = $('input[name=issueURL]').val();

            var isError = false;
            if($('#terms:checked').length == 0){
                _alert({ message: "Please accept the terms of service." });
                isError = true;
            }
            if(issueURL == ''){
                _alert({ message: "Please enter a issue URL." });
                isError = true;
            }
            if(isError){
                return;
            }

            $(this).attr('disabled','disabled');
            var callback = function(error, result){
                if(error){
                    _alert({ message: "Could not get bounty details" });
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
                    } else if(claimeeAddress == '0x0000000000000000000000000000000000000000'){
                        errormsg = "No claimee found for this bounty.";
                    } else if(fromAddress != web3.eth.coinbase){
                        errormsg = "You can only process a bounty if you submitted it.";
                    }

                    if(errormsg){
                        _alert({ message: errormsg });
                        $('.submitBounty').removeAttr('disabled');
                        return;
                    }

                    var _callback = function(error, result){
                        var next = function(){
                            callFunctionWhenTransactionMined(result,function(){
                                sync_web3(issueURL);
                                localStorage[issueURL] = timestamp();
                                add_to_watch_list(issueURL);
                                document.location.href= "/bounty/details?url="+issueURL;
                                _alert({ message: "Transaction complete." }, 'info');
                            });

                        };
                        if(error){
                            _alert({ message: "There was an error" });
                            $('.submitBounty').removeAttr('disabled');
                        } else {
                            next();
                        }
                    };

                    var method = bounty.approveBountyClaim;
                    if(whatAction != 'Accept'){
                        method = bounty.rejectBountyClaim;
                    }
                    method.estimateGas(issueURL, {from :account}, 
                            function(errors,result){
                                var gas = result * 2;
                                var gasLimit = gas * 2;
                                method.sendTransaction(issueURL, 
                                    {from :account, 
                                        gas:gas, 
                                        gasLimit: gasLimit, 
                                        gasPrice:gasPrice}, 
                                    _callback);
                            }
                        );


                }
            };
            bounty.bountydetails.call(issueURL, callback);
            e.preventDefault();
        });
    },100);

};
