$(document).on("click", "#submit_create_token", (event) => {
  event.preventDefault();
  let tokenName = $("#createPTokenName").val();
  let tokenSymbol = $("#createPTokenSymbol").val();
  let tokenPrice = $("#createPTokenPrice").val();
  let tokenSupply = $("#createPTokenSupply").val();

  createPToken(tokenName, tokenSymbol, tokenPrice, tokenSupply);
});

async function createPToken(tokenName, tokenSymbol, tokenPrice, tokenSupply) {
  [user] = await web3.eth.getAccounts();
  const factoryAddress = "0x7bE324A085389c82202BEb90D979d097C5b3f2E8";
  const DAI = "0x0fbe13fcf9c8b33a5c20fa93160ded33d4df702e"
  const factory = await new web3.eth.Contract(
    document.contxt.ptoken_factory_abi,
    factoryAddress
  );

  let result = await factory.methods
    .createPToken(tokenName, tokenSymbol, tokenPrice, tokenSupply, DAI)
    .send({
      from: user,
    });

}
