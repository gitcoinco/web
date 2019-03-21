// on settings/token page

var from = '0x0583858adfe7d1d3DC7F8447301cf7B7b056d638';
var token_address = '0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359';// DAI
var to = '0x2af47a65da8cd66729b4209c22017d6a5c2d2400'; //stdbounties
var token_contract = web3.eth.contract(token_abi).at(token_address);

token_contract.allowance.call(from, to, function(error, result) {
    console.log(result.toString())
});
