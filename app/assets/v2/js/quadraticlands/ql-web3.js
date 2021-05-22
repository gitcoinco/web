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
 *  * @param {uint32} user_id
 *  */
async function isClaimed(user_id) {
  // Get TokenDistributor contract instance
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

/**
 *  * retrieve active proposal counts from GovernorAlpha
 *  *
 *  */
async function proposalState() {
  // Get GovernorAlpha Token contract instance
  const GovernorAlpha = new web3.eth.Contract(
    governor_alpha_abi,
    governor_alpha_address()
  );

  // 1) get total proposal count
  try {
    proposal_count = await GovernorAlpha.methods
      .proposalCount()
      .call({ from: selectedAccount });
  } catch (e) {
    console.error('Could not get proposalCount from GovernorAlpha: ', e);
    return;
  }
  // console.debug('ProposalCount: ', proposal_count);

  // 2) loop through proposals and get state
  var proposal_states = {
    Pending: 0,
    Active: 0,
    Canceled: 0,
    Defeated: 0,
    Succeeded: 0,
    Queued: 0,
    Expired: 0,
    Executed: 0
  };

  for (let proposal = 1; proposal <= proposal_count; proposal++) {
    try {
      proposal_status = await GovernorAlpha.methods
        .state(proposal)
        .call({ from: selectedAccount });
    } catch (e) {
      console.error('Could not get proposal state from GovernorAlpha: ', e);
      return;
    }
    // add to proposal state to object
    bumpCounts(proposal_status);
  }
  // console.debug("proposal_states", proposal_states)
  return proposal_states;

  function bumpCounts(status) {
    if (status == 0) {
      // bump Pending count
      proposal_states.Pending += 1;
    } else if (status == 1) {
      // bump Active count
      proposal_states.Active += 1;
    } else if (status == 2) {
      // bump Canceled count
      proposal_states.Canceled += 1;
    } else if (status == 3) {
      // bump Defeated count
      proposal_states.Defeated += 1;
    } else if (status == 4) {
      // bump Succeeded count
      proposal_states.Succeeded += 1;
    } else if (status == 5) {
      // bump Queued count
      proposal_states.Queued += 1;
    } else if (status == 6) {
      // bump Expired count
      proposal_states.Expired += 1;
    } else if (status == 7) {
      // bump Executed count
      proposal_states.Executed += 1;
    }
  }

}