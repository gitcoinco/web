localStorage['txid'] = '0x274ba28a861463192cb894f7ebb589db4d5d9521dfbd5c9032757582a42f24faTxReceipt'
var issueURL = 'https://github.com/pipermerriam/web3.py/issues/430'
//TODO -- accept stdin

var callback = function (error, result){
console.log(error,result);
};
var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
bounty.bountydetails.call(issueURL, callback);

