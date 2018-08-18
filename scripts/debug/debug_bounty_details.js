// get from bounties.network
var bountyId = 15; // todo - find programmatically
var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

bounty.getBountyData(bountyId, function(error, bountyHash) {
  console.log(error, bountyHash);
});

