load_tokens();

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
    $("input[name=amount]").keyup(retrieveAmount);
    $("input[name=amount]").blur(retrieveAmount);
    $("select[name=deonomination]").change(retrieveAmount);
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
        if(issueURL == ''){
            _alert({ message: "Please enter an issue URL." });
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
        var expire_date = (expirationTimeDelta + (new Date().getTime()/1000|0) );
        ipfs.ipfsApi = IpfsApi({host: 'ipfs.infura.io', port: '5001', protocol: "https", root:'/api/v0'});
        ipfs.setProvider({ host: 'ipfs.infura.io', port: 5001, protocol: 'https', root:'/api/v0'});

        var submit = {
          title: metadata['issueTitle'],
          description: null,
          sourceFileHash: null,
          sourceFileName: null,
          contact: notificationEmail,
          categories: metadata['issueKeywords'],
          githubLink: issueURL,
        };
        ipfs.addJson(submit, function (error, result) {
            if(error){
                mixpanel.track("New Bounty Error", {step: 'post_ipfs', error: error});
                console.error(error);
                _alert({ message: "There was an error.  Please try again or contact support." });
                $('#submitBounty').removeAttr('disabled');
                return;
            }


            bounty.issueAndActivateBounty.estimateGas(
                account, 
                expire_date, 
                result, 
                amount, 
                0x0, 
                false, 
                tokenAddress,
                amount,
                {
                    from :account, 
                    value:amount, 
                },
                function(error,result){
                    var gas = Math.round(result * gasMultiplier);
                    var gasLimit = Math.round(gas * gasLimitMultiplier);
                    bounty.issueAndActivateBounty.sendTransaction(
                        account, 
                        expire_date, 
                        result, 
                        amount, 
                        0x0, 
                        false, 
                        tokenAddress,
                        amount,
                        {
                            from :account, 
                            value:amount, 
                            gas:web3.toHex(gas), 
                            gasLimit: web3.toHex(gasLimit), 
                            gasPrice:web3.toHex(defaultGasPrice),
                        },
                        function(error,result){

                            if(error){
                                mixpanel.track("New Bounty Error", {step: 'post_bounty', error: error});
                                console.error(error);
                                _alert({ message: "There was an error.  Please try again or contact support." });
                                $('#submitBounty').removeAttr('disabled');
                                return;
                            }

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
                    );
                }
            );
        });
    });
});