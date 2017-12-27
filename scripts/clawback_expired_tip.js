// go to gitcoin.co/tip
// unlock metamask

var callback = function (error, result){
var gasLimit = 79992;
console.log(error,result);
};
var idx = '0x9599d43f1a183714e5c49fde33b196c79880dafb';
contract().expireTransfer(idx,callback);
