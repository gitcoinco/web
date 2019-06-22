// go to https://gitcoin.co/kudos/send/?id=77
// unlock metamask

var kudos_contract = web3.eth.contract(kudos_abi).at(kudos_address());
var kudos_token_id = 11111;

var callback = function(error, result) {
  console.log(result[0].toNumber());
  console.log(result[1].toNumber());
  console.log(result[2].toNumber());
  console.log(result[3].toNumber());
};

var callback2 = function(error, result) {
  console.log(result);
};

// to confirm which kudos youre looking at
kudos_contract.tokenURI(kudos_token_id, callback2);
kudos_contract.ownerOf(kudos_token_id, callback2);

// to actually do transfer

kudos_contract.safeTransferFrom("0x000000", "0x000000", kudos_token_id, callback2);


