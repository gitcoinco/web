// get from bounties.network
var bountyId = 15; // todo - find programmatically
const contract_version = '1';
var bounty = web3.eth.contract(getBountyABI(contract_version)).at(bounty_address());

bounty.getBountyData(bountyId, function(error, bountyHash) {
  console.log(error, bountyHash);
});

