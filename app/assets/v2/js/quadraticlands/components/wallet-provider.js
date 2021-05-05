document.addEventListener('DOMContentLoaded', function() {

  const token_balance = document.querySelector('#token_balance');
  const token_symbol = document.querySelector('#token_symbol');

  document.addEventListener('dataWalletReady', walletMenu);

});


async function walletMenu() {

  try {
    let balance = await getTokenBalances(gtc_address());

    token_balance.innerHTML = balance.balance.toFixed(2);
    token_symbol.innerHTML = balance.symbol;
  } catch (e) {
    console.log(e);
  }

}
