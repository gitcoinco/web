// on tips page
var bounty = contract()

var _idx = '0xa8ec82449eaadc71921d1ac7609e89e0a2453742';

contract().expireTransfer(_idx, function(error, result) {
    console.log(error,result);
});
