// go to gitcoin.co/tip
// unlock metamask

var callback = function(error, result) {
  console.log('active', result[0]);
  console.log('amount', result[1].toNumber());
  console.log('tip dev', result[2].toNumber());
  console.log('initialized', result[3]);
  console.log('expiry time', result[4].toNumber());
  console.log('from', result[5]);
  console.log('owner', result[6]);
  console.log('erc20 contract', result[7]);
};
var idx = '0x0';

contract().getTransferDetails.call(idx, callback);
