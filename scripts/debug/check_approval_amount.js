// on settings/token page

var from = '0x7d96b5c4279e20bab1ca0043a65f2bb156b0c6eb';
var token_address = '0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359';// DAI
var to = '0x2af47a65da8cd66729b4209c22017d6a5c2d2400'; //stdbounties
var token_contract = web3.eth.contract(token_abi).at(token_address);

token_contract.allowance.call(from, to, function(error, result) {
    console.log(result.toString())
});
