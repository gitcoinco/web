load_tokens();
var setUsdAmount= function (event) {
    var amount  = $('input[name=amount]').val();
    var denomination  = $('#token option:selected').text();
    var estimate = getUSDEstimate(amount, denomination, function(estimate){
        $('#usd_amount').html(estimate);
    });
};

// Wait until page is loaded, then run the function
$(document).ready(function(){
    // Load sidebar radio buttons from localStorage
    if(getParam('source')){
        $('input[name=issueURL]').val(getParam('source'));
    } else if(getParam('url')){
        $('input[name=issueURL]').val(getParam('url'));
    } else if(localStorage['issueURL']){
         $('input[name=issueURL]').val(localStorage['issueURL']);
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
    
    //fetch issue URL related info
    $("input[name=amount]").keyup(setUsdAmount);
    $("input[name=amount]").blur(setUsdAmount);
    $("select[name=deonomination]").change(setUsdAmount);
    $("input[name=issueURL]").blur(retrieveTitle);
    $("input[name=issueURL]").blur(retrieveKeywords);
    $("input[name=issueURL]").blur(retrieveDescription);

    if($("input[name=issueURL]").val()!=''){
        retrieveTitle();
        retrieveKeywords();
        retrieveDescription();
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
        var tokenAddress = $('select[name=deonomination]').val();
        var token = tokenAddressToDetails(tokenAddress);
        var decimals = token['decimals'];
        var tokenName = token['name'];
        var decimalDivisor = Math.pow( 10, decimals );
        var expirationTimeDelta = $('select[name=expirationTimeDelta').val();

       var metadata = {
            issueTitle : $('input[name=title').val(),
            issueDescription : $('textarea[name=description').val(),
            issueKeywords : $('input[name=keywords').val(),
            tokenName : tokenName,
            githubUsername : githubUsername,
            notificationEmail : notificationEmail,
            fullName: $('input[name=fullName').val(),
            experienceLevel : $('select[name=experienceLevel').val(),
            projectLength : $('select[name=projectLength').val(),
            bountyType : $('select[name=bountyType').val(),
        }

        // https://github.com/ConsenSys/StandardBounties/issues/21
        var ipfsBounty = {
            payload: {
                title: metadata.issueTitle,
                description: metadata.issueDescription,
                sourceFileName: "",
                sourceFileHash: "",
                sourceDirectoryHash: "",
                issuer: {
                    name: metadata.fullName,
                    email: metadata.notificationEmail,
                    githubUsername: metadata.githubUsername,
                    address: '', // Fill this in later
                },
                funders:[
                ],
                categories: metadata.issueKeywords.split(","),
                created: new Date().getTime()/1000|0,
                webReferenceURL: issueURL,
                // optional fields
                metadata: metadata,
                tokenName: tokenName,
                tokenAddress: tokenAddress,
            },
            meta: {
                platform: 'gitcoin',
                schemaVersion: '0.1',
                schemaName: 'gitcoinBounty',
            },
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
        localStorage.removeItem('bountyId');


        //setup web3
        // TODO: web3 is using the web3.js file.  In the future we will move
        // to the node.js package.  github.com/ethereum/web3.js
        var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
        var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
        var account = web3.eth.coinbase;
        amount = amount * decimalDivisor;
        // Create the bounty object.
        // This function instantiates a contract from the existing deployed Standard Bounties Contract.
        // bounty_abi is a giant object containing the different network options
        // bounty_address() is a function that looks up the name of the network and returns the hash code
        var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
        // StandardBounties integration begins here
        var expire_date = (parseInt(expirationTimeDelta) + (new Date().getTime()/1000|0) );
        // Set up Interplanetary file storage
        // IpfsApi is defined in the ipfs-api.js.
        // Is it better to use this JS file than the node package?  github.com/ipfs/
        ipfs.ipfsApi = IpfsApi({host: 'ipfs.infura.io', port: '5001', protocol: "https", root:'/api/v0'});
        ipfs.setProvider({ host: 'ipfs.infura.io', port: 5001, protocol: 'https', root:'/api/v0'});

        // setup inter page state
        localStorage[issueURL] = JSON.stringify({
            'timestamp': null,
            'dataHash': null,
            'issuer': account,
            'txid': null,
        });  

        function syncDb() {
            // Need to pass the bountydetails as well, since I can't grab it from the 
            // Standard Bounties contract.
            dataLayer.push({'event': 'fundissue'});
            sync_web3(issueURL);  // Writes the bounty URL to the database
            
            // update localStorage issuePackage
            var issuePackage = JSON.parse(localStorage[issueURL]);
            issuePackage['timestamp'] = timestamp();
            localStorage[issueURL] = JSON.stringify(issuePackage);

            _alert({ message: "Submission sent to web3." }, 'info');
            setTimeout(function(){
                delete localStorage['issueURL'];
                mixpanel.track("Submit New Bounty Success", {});
                document.location.href= "/funding/details/?url="+issueURL;
            },1000);
        }

        // web3 callback
        function web3Callback (error,result){

            if(error){
                mixpanel.track("New Bounty Error", {step: 'post_bounty', error: error});
                console.error(error);
                _alert({ message: "There was an error.  Please try again or contact support." });
                unloading_button($('#submitBounty'));
                return;
            }

            // update localStorage issuePackage
            var issuePackage = JSON.parse(localStorage[issueURL]);
            issuePackage['txid'] = result;
            localStorage[issueURL] = JSON.stringify(issuePackage);

            //sync db
            syncDb();

        }

        function newIpfsCallback (error, result) {
            if(error){
                mixpanel.track("New Bounty Error", {step: 'post_ipfs', error: error});
                console.error(error);
                _alert({ message: "There was an error.  Please try again or contact support." });
                unloading_button($('#submitBounty'));
                return;
            }

            // cache data hash to find bountyId later
            // update localStorage issuePackage
            var issuePackage = JSON.parse(localStorage[issueURL]);
            issuePackage['dataHash'] = result;
            localStorage[issueURL] = JSON.stringify(issuePackage);
            
            // bounty is a web3.js eth.contract address
            // The Ethereum network requires using ether to do stuff on it
            // issueAndActivateBounty is a method definied in the StandardBounties solidity contract.

            var eth_amount = isETH ? amount : 0
            var _paysTokens = !isETH;
            var bountyIndex = bounty.issueAndActivateBounty(
                account,            // _issuer
                expire_date,        // _deadline
                result,             // _data (ipfs hash)
                amount,             // _fulfillmentAmount
                0x0,                // _arbiter
                _paysTokens,              // _paysTokens
                tokenAddress,       // _tokenContract
                amount,             // _value
                {                   // {from: x, to: y}
                    from :account,
                    value: eth_amount,
                    gasPrice: web3.toHex($("#gasPrice").val()) * Math.pow( 10, 9 ),
                },
                web3Callback        // callback for web3
            );
        }
        // Check if the bounty already exists
        var uri = '/api/v0.1/bounties/?github_url='+issueURL;
        $.get(uri, function(results, status){
            results = sanitizeAPIResults(results);
            var result = results[0];
            if (result != null) {
                _alert({ message: "A bounty already exists for that Github Issue." });
                unloading_button($('#submitBounty'));
                return;
            } else {

                var approve_success_callback = function(callback){
                    // Add data to IPFS and kick off all the callbacks.
                    ipfsBounty.payload.issuer.address = account;
                    ipfs.addJson(ipfsBounty, newIpfsCallback);
                };
                if(isETH){
                    //no approvals needed for ETH
                    approve_success_callback();
                } else {
                    token_contract.approve(bounty_address(), amount, {from:account, value:0, gasPrice:web3.toHex($("#gasPrice").val()) * 10**9}, approve_success_callback)
                }

            }
        });
    });
});
