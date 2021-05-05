/**
 *  * Gets the delegateAddress for active account
 *  * @param {string} selectedAccount - active wallet address
 *  */
async function getDelegateAddress(tokenAddress, selectedAccount) {
  // Get GTC Token contract instance
  let GTCContract = new web3.eth.Contract(gtc_token_abi, tokenAddress);

  // Call getCurrentVotes function
  try {
    delegate_address = GTCContract.methods
      .delegates(selectedAccount)
      .call({ from: selectedAccount });
  } catch (e) {
    console.error('Could not get Delegate Address: ', e);
    return;
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
    current_votes = GTCContract.methods
      .getCurrentVotes(selectedAccount)
      .call({ from: selectedAccount });
  } catch (e) {
    console.error('Could not get prior votes: ', e);
    return;
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
    past_votes = GTCContract.methods
      .getPriorVotes(account, block_number)
      .call({ from: selectedAccount });
  } catch (e) {
    console.error('Could not get prior votes: ', e);
    return;
  }
  return past_votes;
}

/**
 *  * Sets delegate address
 *  * @param string
 *  */
async function setDelegateAddress(_delegateAddress, tokenAddress) {
  // Get GTC Token contract instance
  let GTC = new web3.eth.Contract(gtc_token_abi, tokenAddress);

  try {
    const setDelegate = () => {
      GTC.methods
        .delegate(_delegateAddress)
        .send({ from: selectedAccount, gasLimit: '300000' })
        .on('transactionHash', async function(transactionHash) {
          updateInterface('pending', transactionHash);
          console.debug('ON TRANSACTION HASH - PENDING', transactionHash);
        })
        .on('confirmation', (confirmationNumber) => {
          if (confirmationNumber >= 0) {
            updateInterface('success');
            console.debug('ON CONFIRMATION');
          }
        })
        .on('error', (error) => {
          updateInterface('error');
          console.error('Error setting delegate address:', error);
        });
    };

    setDelegate();
  } catch {
    console.error('Error setting delegate address!');
  }
}

/**
 *  * calls the isClaimed function on TokenDistributor
 *  * @param {uint32} user_id (will maybe change to uint256)
 *  */
async function isClaimed(user_id) {
  // Get GTC Token contract instance
  const TokenDistributor = new web3.eth.Contract(
    token_distributor_abi,
    token_distributor_address()
  );

  // Call getCurrentVotes function
  try {
    is_claimed = TokenDistributor.methods
      .isClaimed(user_id)
      .call({ from: selectedAccount });
  } catch (e) {
    console.error('Could not get claim state from TokenDistributor: ', e);
    return;
  }
  return is_claimed;
}