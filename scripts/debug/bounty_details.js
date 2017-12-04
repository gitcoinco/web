var issueURL = 'https://github.com/pipermerriam/web3.py/issues/302'
//TODO -- accept stdin

var callback = function (error, result){
console.log(error,result);
};
var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
bounty.bountydetails.call(issueURL, callback);

