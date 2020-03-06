// go to gitcoin.co/tip
// unlock metamask

var callback = function(error, result) {
  // eslint-disable-next-line no-console
  console.log(result);
  // eslint-disable-next-line no-console
  console.log(web3.toAscii(result['input']));
};
var transactionHash = '0x0';

web3.eth.getTransaction(transactionHash, callback);

// eslint-disable-next-line no-redeclare
var callback = function(error, result) {
  // eslint-disable-next-line no-console
  console.log(result);
};

web3.eth.getTransactionReceipt(transactionHash, callback);
