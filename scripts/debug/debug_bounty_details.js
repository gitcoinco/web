// Fetch Bounty Data std bounties contract

// PARAMS TO BE UPDATED
const bounty_id = 15;
const contract_version = '1';

const bounty = web3.eth.contract(
  getBountyABI(contract_version)
).at(bounty_address(contract_version));

if (contract_version == '2') {
  bounty.getBounty(bounty_id, (error, data) => {
    console.log(error, data);
  })
} else {
  bounty.getBountyData(bounty_id, (error, data) => {
    console.log(error, data);
  });
}