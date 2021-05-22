document.addEventListener('DOMContentLoaded', function() {
  const token = document.querySelector('#wallet-provider .token');
  const token_balance = document.querySelector('#token_balance');
  const token_symbol = document.querySelector('#token_symbol');

  document.addEventListener('dataWalletReady', async function() {

    try {
      let balance = await getTokenBalances(gtc_address());

      token_balance.innerHTML = balance.balance.toFixed(2);
      token_symbol.innerHTML = balance.symbol;
    } catch (e) {
      token.style.display = 'none';

      console.log(e);
    }
  });

});
