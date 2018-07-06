// go to gitcoin.co/tip
// unlock metamask

var callback = function(error, result) {
  console.log(result);
  console.log(web3.toAscii(result['input']));
};
var transactionHash = '0x0';

web3.eth.getTransaction(transactionHash, callback);

var callback = function(error, result) {
  console.log(result);
};

web3.eth.getTransactionReceipt(transactionHash, callback);
