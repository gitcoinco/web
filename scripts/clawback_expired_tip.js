// go to gitcoin.co/tip
// unlock metamask

var callback = function(error, result) {
  var gasLimit = 79992;

  console.log(error, result);
};

var idx = '0xc1ca04bfc1d601cd1fb2f4d38b0ea780da16bc92';

contract().expireTransfer(idx, callback);
