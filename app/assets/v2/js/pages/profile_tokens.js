const factoryAddress = '0x7bE324A085389c82202BEb90D979d097C5b3f2E8';
const DAI = '0x6b67DD1542ef11153141037734D21E7Cbd7D9817';

$(document).on('click', '#submit_buy_token', (event) => {
  event.preventDefault();
  const form = $('#ptokenBuyForm')[0];

  if (form.checkValidity() === false) {
    event.stopPropagation();
    _alert('You must agree before submitting', 'error', 2000);
    return;
  }

  buyPToken($('#ptokenAmount').val());
});

$(document).on('input', '#ptokenRedeemAmount', (event) => {
  event.preventDefault();
  const amount = $(event.target).val();

  $('#ptokenRedeemCost').text(`${document.current_ptoken_value * parseFloat(amount) || 0} DAI`);
  $('#redeem-amount').text(parseFloat(amount));
});

$(document).on('input', '#ptokenAmount', (event) => {
  event.preventDefault();
  const amount = $(event.target).val();

  $('#ptokenCost').text(`${document.current_ptoken_value * parseFloat(amount) || 0} DAI`);
  $('#buy-amount').text(amount);
});

$(document).on('click', '#submit_redeem_token', (event) => {
  event.preventDefault();
  const form = $('#ptokenRedeemForm')[0];
  const amountField = $(form.ptokenRedeemAmount);
  const tos = $(form.ptokenRedeemTerms);
  const redeem_amount = parseFloat(amountField.val());

  if (!tos.prop('checked')) {
    event.stopPropagation();
    _alert('You must agree before submitting', 'error', 2000);
    tos.addClass('is-invalid');
    return;
  }
  tos.removeClass('is-invalid');

  if (isNaN(redeem_amount)) {
    _alert(`Provide a valid amount no greater than ${document.current_hodling} ${document.current_ptoken_symbol}`, 'error', 2000);
    amountField.addClass('is-invalid');
    return;
  } else if (document.current_hodling === 0) {
    _alert(`You don't have ${document.current_ptoken_symbol} tokens`, 'error', 2000);
    amountField.addClass('is-invalid');
    return;
  } else if (redeem_amount > document.current_hodling) {
    _alert(`You can't redeem more than ${document.current_hodling}  ${document.current_ptoken_symbol}`, 'error', 2000);
    amountField.addClass('is-invalid');
    return;
  }
  amountField.removeClass('is-invalid');

  redeemPToken($('#ptokenRedeemAmount').val());
});

async function buyPToken(tokenAmount) {
  [user] = await web3.eth.getAccounts();
  const pToken = await new web3.eth.Contract(
    document.contxt.ptoken_abi, // TODO: contxt.ptoken_abi needs to be implemented.
    pTokenAddress // TODO: this needs to be derived from the profile page
  );

  pToken.methods
    .purchase(tokenAmount)
    .send({
      from: user
    })
    .on('transactionHash', function(transactionHash) {
      purchase_ptoken(
        tokenId, // TODO: determine token ID based on profile
        tokenAmount,
        user,
        (new Date()).toISOString(),
        transactionHash
      );
    });
}

async function redeemPToken(tokenAmount) {
  [user] = await web3.eth.getAccounts();
  const pToken = await new web3.eth.Contract(
    document.contxt.ptoken_abi, // TODO: contxt.ptoken_abi needs to be implemented.
    pTokenAddress // TODO: this needs to be derived from the profile page
  );

  pToken.methods
    .redeem(tokenAmount)
    .send({
      from: user
    })
    .on('transactionHash', function(transactionHash) {
      request_redemption(pTokenId, tokenAmount, network); // TODO: determine token ID and network
    });
}
