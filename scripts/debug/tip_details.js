// on tips page
var bounty = contract()

var _idx = '0x2e14ae415a17a269c6f3d6ed2b9b5c84d82f36eb';

contract().expireTransfer(_idx, function(error, result) {
    console.log(error,result);
});
