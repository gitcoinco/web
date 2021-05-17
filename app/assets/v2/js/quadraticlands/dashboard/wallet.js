document.addEventListener('DOMContentLoaded', function() {

  // every time web3 is ready / address changes this calls the async function delegationInterface()
  document.addEventListener('dataWalletReady', walletInterface);

  const dashboard_wallet_address = document.getElementById('dashboard_wallet_address');
  const dashboard_wallet_token_balance = document.getElementById('dashboard_wallet_token_balance');
  const dashboard_wallet_token_symbol = document.getElementById('dashboard_wallet_token_symbol');
  const dashboard_wallet_voting_power = document.getElementById('dashboard_wallet_voting_power');
  const dashboard_wallet_delegate_address = document.getElementById('dashboard_wallet_delegate_address');

});


async function walletInterface() {

  try {

    let balance = await getTokenBalances(gtc_address());

    dashboard_wallet_token_balance.innerHTML = balance.balance.toFixed(2);
    dashboard_wallet_token_symbol.innerHTML = balance.symbol;
    dashboard_wallet_address.innerHTML = truncate(selectedAccount);

    let voting_power = await getCurrentVotes(gtc_address());

    voting_power = voting_power / 10 ** 18;
    dashboard_wallet_voting_power.innerHTML = voting_power.toFixed(2);

    let delegateAddress = await getDelegateAddress(gtc_address(), selectedAccount);

    if (delegateAddress != selectedAccount) {
      dashboard_wallet_delegate_address.innerHTML = '&rarr; ' + truncate(delegateAddress);
    } else {
      dashboard_wallet_delegate_address.innerHTML = '';
    }
    
    // get proposal states from GovernorAlpha
    let proposal_states = await proposalState();
    const stats_on_chain = document.getElementById('stats-on-chain');
    stats_on_chain.innerHTML = proposal_states.Active;
    if (proposal_states.Active >= 1) {
      stats_on_chain.classList.add('aqua');
    }


  } catch (e) {
    console.error(e);
  }

}
