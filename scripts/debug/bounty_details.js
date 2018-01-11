//TODO -- accept stdin
var issueURL = 'https://github.com/MarketProject/dApps/issues/7'
localStorage[issueURL] = timestamp();

var callback = function (error, result){
console.log(error,result);
};
var bounty_contract = web3.eth.contract(bounty_abi).at(bounty_address());
bounty_contract.bountydetails.call(issueURL, callback);

