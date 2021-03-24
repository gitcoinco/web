
function web3Ready() {
    console.debug('WEB3 version from script', web3.version);

    //window.addEventListener('dataWalletReady', function(e) {
    $('#wallet-address').html(selectedAccount)
    
	// }, false);
    // some examples of getting data from the GTC and tokenDist contracts 

    // get token balance - (using generic ERC20 function from Octos wallet file)
    getTokenBalances(gtc_address()).then(function(result) {
        console.debug('ERC20 TokenBalance:', result.balance);
        $('#gtc-token-balance').html(result.balance)
    });

    // get current votes 
    getCurrentVotes(gtc_address()).then(function(result) { 
        console.debug('Current GTC Votes:', result);
    });

    // get prior votes by block number 
    block_number = 4242424
    getPriorVotes(gtc_address(), selectedAccount, block_number).then(function(result) { 
       console.debug('Current GTC Votes:', result);
    });

    // get delegate address
    getDelegateAddress(gtc_address(), selectedAccount).then(function(result) {
        console.debug('SelectedAccount Delegate Address: ', result);
    });
}

// dataWalletReady comes from wallet.js function 
document.addEventListener("dataWalletReady", web3Ready);


/**
*  * Gets the delegateAddress for active account 
*  * @param {string} selectedAccount - active wallet address
*  */
async function getDelegateAddress(tokenAddress, selectedAccount) {

    // Get GTC Token contract instance
    let GTCContract = new web3.eth.Contract(gtc_token_abi, tokenAddress);
    
    // Call getCurrentVotes function
    try {
        delegate_address = GTCContract.methods.delegates(selectedAccount).call({from: selectedAccount})
    } catch(e) {
        console.log('Could not get Delegate Address: ', e);
        return
    }
    return delegate_address;
}


/**
*  * Gets the current votes balance for an address from GTC Token contract.
*  * @param {string} tokenAddress - the ERC20 token address
*  */
async function getCurrentVotes(tokenAddress) {

    // Get GTC Token contract instance
    let GTCContract = new web3.eth.Contract(gtc_token_abi, tokenAddress);
    
    // Call getCurrentVotes function
    try {
        current_votes = GTCContract.methods.getCurrentVotes(selectedAccount).call({from: selectedAccount})
    } catch(e) {
        console.log('Could not get prior votes: ', e);
        return
    }
    return current_votes;
}

/**
*  * Gets the past votes balance at a given block for an address from GTC Token contract 
*  * @param {string} tokenAddress - the ERC20 token address
*  */
async function getPriorVotes(tokenAddress, account, block_number) {

    // Get GTC Token contract instance
    let GTCContract = new web3.eth.Contract(gtc_token_abi, tokenAddress);
    
    // Call getPriorVotes function
    try {
        past_votes = GTCContract.methods.getPriorVotes(account, block_number).call({from: selectedAccount})
    } catch (e) {
        console.log('Could not get prior votes: ', e);
        return;
    }
    return past_votes;
}

