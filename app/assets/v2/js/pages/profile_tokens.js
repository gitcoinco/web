$(document).on("click", "#submit_create_token", (event) => {
  event.preventDefault();
  let tokenName = $("#createPTokenName").val();
  let tokenSymbol = $("#createPTokenSymbol").val();
  let tokenPrice = $("#createPTokenPrice").val();
  let tokenSupply = $("#createPTokenSupply").val();

  deployToken(tokenName, tokenSymbol, tokenPrice, tokenSupply);
});

async function deployToken(tokenName, tokenSymbol, tokenPrice, tokenSupply) {
  console.log("Deploying token");
  [user] = await web3.eth.getAccounts();
  const factoryAddress = "0x7bE324A085389c82202BEb90D979d097C5b3f2E8";
  const factory = await new web3.eth.Contract(ptoken_abi.abi, factoryAddress);

  await factory.methods
    .createPToken(tokenName, tokenSymbol, tokenPrice, tokenSupply)
    .send({
      from: user,
    });
}
