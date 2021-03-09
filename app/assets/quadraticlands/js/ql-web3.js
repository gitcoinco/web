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
