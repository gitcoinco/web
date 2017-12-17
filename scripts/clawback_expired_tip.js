var callback = function (error, result){
var gasLimit = 79992;
console.log(error,result);
};
var idx = '0x774d782544e5c1f8788420f065d9680e7ab97c09';
contract().expireTransfer.sendTransaction(idx,{gasLimit:gasLimit},callback);
