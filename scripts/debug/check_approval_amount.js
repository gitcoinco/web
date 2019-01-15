// on settings/token page

var from = '0x78040ab06e05f59fd78ca7367cbf4e95069cac47';
var token_address = '0x2af47a65da8cd66729b4209c22017d6a5c2d2400';
var to = '0x2af47a65da8cd66729b4209c22017d6a5c2d2400';
var token_contract = web3.eth.contract(token_abi).at(token_address);
var from = web3.eth.coinbase;

token_contract.allowance.call(from, to, function(error, result) {
    console.log(result.toNumber())
});
