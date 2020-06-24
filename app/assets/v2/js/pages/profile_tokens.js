const factoryAddress = '0x7bE324A085389c82202BEb90D979d097C5b3f2E8';
const DAI = '0x6b67DD1542ef11153141037734D21E7Cbd7D9817';

$(document).on('click', '#submit_buy_token', (event) => {
  event.preventDefault();
  buyPToken($('#ptokenAmount').val());
});

$(document).on('click', '#submit_redeem_token', (event) => {
  event.preventDefault();
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
