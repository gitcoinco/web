var token_abi = [{'inputs': [], 'constant': true, 'name': 'mintingFinished', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'name', 'outputs': [{'type': 'string', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_spender'}, {'type': 'uint256', 'name': '_value'}], 'constant': false, 'name': 'approve', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'totalSupply', 'outputs': [{'type': 'uint256', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_from'}, {'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_value'}], 'constant': false, 'name': 'transferFrom', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'decimals', 'outputs': [{'type': 'uint8', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_amount'}], 'constant': false, 'name': 'mint', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'version', 'outputs': [{'type': 'string', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_owner'}], 'constant': true, 'name': 'balanceOf', 'outputs': [{'type': 'uint256', 'name': 'balance'}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': false, 'name': 'finishMinting', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'owner', 'outputs': [{'type': 'address', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [], 'constant': true, 'name': 'symbol', 'outputs': [{'type': 'string', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_value'}], 'constant': false, 'name': 'transfer', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_owner'}, {'type': 'address', 'name': '_spender'}], 'constant': true, 'name': 'allowance', 'outputs': [{'type': 'uint256', 'name': 'remaining'}], 'payable': false, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': 'newOwner'}], 'constant': false, 'name': 'transferOwnership', 'outputs': [], 'payable': false, 'type': 'function'}, {'payable': false, 'type': 'fallback'}, {'inputs': [{'indexed': true, 'type': 'address', 'name': 'to'}, {'indexed': false, 'type': 'uint256', 'name': 'amount'}], 'type': 'event', 'name': 'Mint', 'anonymous': false}, {'inputs': [], 'type': 'event', 'name': 'MintFinished', 'anonymous': false}, {'inputs': [{'indexed': true, 'type': 'address', 'name': 'owner'}, {'indexed': true, 'type': 'address', 'name': 'spender'}, {'indexed': false, 'type': 'uint256', 'name': 'value'}], 'type': 'event', 'name': 'Approval', 'anonymous': false}, {'inputs': [{'indexed': true, 'type': 'address', 'name': 'from'}, {'indexed': true, 'type': 'address', 'name': 'to'}, {'indexed': false, 'type': 'uint256', 'name': 'value'}], 'type': 'event', 'name': 'Transfer', 'anonymous': false}];
var bounty_abi = [{'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}], 'name': 'killBounty', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}], 'name': 'getBountyToken', 'outputs': [{'name': '', 'type': 'address'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_data', 'type': 'string'}], 'name': 'fulfillBounty', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newDeadline', 'type': 'uint256'}], 'name': 'extendDeadline', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': true, 'inputs': [], 'name': 'getNumBounties', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_fulfillmentId', 'type': 'uint256'}, {'name': '_data', 'type': 'string'}], 'name': 'updateFulfillment', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newFulfillmentAmount', 'type': 'uint256'}, {'name': '_value', 'type': 'uint256'}], 'name': 'increasePayout', 'outputs': [], 'payable': true, 'stateMutability': 'payable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newFulfillmentAmount', 'type': 'uint256'}], 'name': 'changeBountyFulfillmentAmount', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newIssuer', 'type': 'address'}], 'name': 'transferIssuer', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_value', 'type': 'uint256'}], 'name': 'activateBounty', 'outputs': [], 'payable': true, 'stateMutability': 'payable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_issuer', 'type': 'address'}, {'name': '_deadline', 'type': 'uint256'}, {'name': '_data', 'type': 'string'}, {'name': '_fulfillmentAmount', 'type': 'uint256'}, {'name': '_arbiter', 'type': 'address'}, {'name': '_paysTokens', 'type': 'bool'}, {'name': '_tokenContract', 'type': 'address'}], 'name': 'issueBounty', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_issuer', 'type': 'address'}, {'name': '_deadline', 'type': 'uint256'}, {'name': '_data', 'type': 'string'}, {'name': '_fulfillmentAmount', 'type': 'uint256'}, {'name': '_arbiter', 'type': 'address'}, {'name': '_paysTokens', 'type': 'bool'}, {'name': '_tokenContract', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'issueAndActivateBounty', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': true, 'stateMutability': 'payable', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}], 'name': 'getBountyArbiter', 'outputs': [{'name': '', 'type': 'address'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_value', 'type': 'uint256'}], 'name': 'contribute', 'outputs': [], 'payable': true, 'stateMutability': 'payable', 'type': 'function'}, {'constant': true, 'inputs': [], 'name': 'owner', 'outputs': [{'name': '', 'type': 'address'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newPaysTokens', 'type': 'bool'}, {'name': '_newTokenContract', 'type': 'address'}], 'name': 'changeBountyPaysTokens', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}], 'name': 'getBountyData', 'outputs': [{'name': '', 'type': 'string'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_fulfillmentId', 'type': 'uint256'}], 'name': 'getFulfillment', 'outputs': [{'name': '', 'type': 'bool'}, {'name': '', 'type': 'address'}, {'name': '', 'type': 'string'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newArbiter', 'type': 'address'}], 'name': 'changeBountyArbiter', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newDeadline', 'type': 'uint256'}], 'name': 'changeBountyDeadline', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_fulfillmentId', 'type': 'uint256'}], 'name': 'acceptFulfillment', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '', 'type': 'uint256'}], 'name': 'bounties', 'outputs': [{'name': 'issuer', 'type': 'address'}, {'name': 'deadline', 'type': 'uint256'}, {'name': 'data', 'type': 'string'}, {'name': 'fulfillmentAmount', 'type': 'uint256'}, {'name': 'arbiter', 'type': 'address'}, {'name': 'paysTokens', 'type': 'bool'}, {'name': 'bountyStage', 'type': 'uint8'}, {'name': 'balance', 'type': 'uint256'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}], 'name': 'getBounty', 'outputs': [{'name': '', 'type': 'address'}, {'name': '', 'type': 'uint256'}, {'name': '', 'type': 'uint256'}, {'name': '', 'type': 'bool'}, {'name': '', 'type': 'uint256'}, {'name': '', 'type': 'uint256'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'constant': false, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}, {'name': '_newData', 'type': 'string'}], 'name': 'changeBountyData', 'outputs': [], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': true, 'inputs': [{'name': '_bountyId', 'type': 'uint256'}], 'name': 'getNumFulfillments', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'name': '_owner', 'type': 'address'}], 'payable': false, 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}], 'name': 'BountyIssued', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}, {'indexed': false, 'name': 'issuer', 'type': 'address'}], 'name': 'BountyActivated', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}, {'indexed': true, 'name': 'fulfiller', 'type': 'address'}, {'indexed': true, 'name': '_fulfillmentId', 'type': 'uint256'}], 'name': 'BountyFulfilled', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': '_bountyId', 'type': 'uint256'}, {'indexed': false, 'name': '_fulfillmentId', 'type': 'uint256'}], 'name': 'FulfillmentUpdated', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}, {'indexed': true, 'name': 'fulfiller', 'type': 'address'}, {'indexed': true, 'name': '_fulfillmentId', 'type': 'uint256'}], 'name': 'FulfillmentAccepted', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}, {'indexed': true, 'name': 'issuer', 'type': 'address'}], 'name': 'BountyKilled', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}, {'indexed': true, 'name': 'contributor', 'type': 'address'}, {'indexed': false, 'name': 'value', 'type': 'uint256'}], 'name': 'ContributionAdded', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}, {'indexed': false, 'name': 'newDeadline', 'type': 'uint256'}], 'name': 'DeadlineExtended', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': 'bountyId', 'type': 'uint256'}], 'name': 'BountyChanged', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': '_bountyId', 'type': 'uint256'}, {'indexed': true, 'name': '_newIssuer', 'type': 'address'}], 'name': 'IssuerTransferred', 'type': 'event'}, {'anonymous': false, 'inputs': [{'indexed': false, 'name': '_bountyId', 'type': 'uint256'}, {'indexed': false, 'name': '_newFulfillmentAmount', 'type': 'uint256'}], 'name': 'PayoutIncreased', 'type': 'event'}];
var kudos_abi = [{"constant":true,"inputs":[{"name":"_interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"cloneFeePercentage","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"InterfaceId_ERC165","outputs":[{"name":"","type":"bytes4"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"isMintable","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"exists","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_index","type":"uint256"}],"name":"tokenByIndex","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"kudos","outputs":[{"name":"priceFinney","type":"uint256"},{"name":"numClonesAllowed","type":"uint256"},{"name":"numClonesInWild","type":"uint256"},{"name":"clonedFromId","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"},{"name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"}],"name":"OwnershipRenounced","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":true,"name":"_tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_approved","type":"address"},{"indexed":true,"name":"_tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_operator","type":"address"},{"indexed":false,"name":"_approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_priceFinney","type":"uint256"},{"name":"_numClonesAllowed","type":"uint256"},{"name":"_tokenURI","type":"string"}],"name":"mint","outputs":[{"name":"tokenId","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"},{"name":"_numClonesRequested","type":"uint256"}],"name":"clone","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"name":"_owner","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"burn","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_cloneFeePercentage","type":"uint256"}],"name":"setCloneFeePercentage","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_isMintable","type":"bool"}],"name":"setMintable","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_tokenId","type":"uint256"},{"name":"_newPriceFinney","type":"uint256"}],"name":"setPrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"getKudosById","outputs":[{"name":"priceFinney","type":"uint256"},{"name":"numClonesAllowed","type":"uint256"},{"name":"numClonesInWild","type":"uint256"},{"name":"clonedFromId","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"getNumClonesInWild","outputs":[{"name":"numClonesInWild","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getLatestId","outputs":[{"name":"tokenId","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}];
var ptoken_abi = [{ anonymous: false, inputs: [ { indexed: false, internalType: "contract PToken", name: "token", type: "address", }, ], name: "NewPToken", type: "event", }, { inputs: [ { internalType: "string", name: "_name", type: "string", }, { internalType: "string", name: "_symbol", type: "string", }, { internalType: "uint256", name: "_cost", type: "uint256", }, { internalType: "uint256", name: "_supply", type: "uint256", }, ], name: "createPToken", outputs: [], stateMutability: "nonpayable", type: "function"}];
// var gtc_token_abi = [ { "inputs":[ { "internalType":"address", "name":"account", "type":"address" }, { "internalType":"address", "name":"minter_", "type":"address" }, { "internalType":"uint256", "name":"mintingAllowedAfter_", "type":"uint256" } ], "stateMutability":"nonpayable", "type":"constructor" }, { "anonymous":false, "inputs":[ { "indexed":true, "internalType":"address", "name":"owner", "type":"address" }, { "indexed":true, "internalType":"address", "name":"spender", "type":"address" }, { "indexed":false, "internalType":"uint256", "name":"amount", "type":"uint256" } ], "name":"Approval", "type":"event" }, { "anonymous":false, "inputs":[ { "indexed":true, "internalType":"address", "name":"delegator", "type":"address" }, { "indexed":true, "internalType":"address", "name":"fromDelegate", "type":"address" }, { "indexed":true, "internalType":"address", "name":"toDelegate", "type":"address" } ], "name":"DelegateChanged", "type":"event" }, { "anonymous":false, "inputs":[ { "indexed":true, "internalType":"address", "name":"delegate", "type":"address" }, { "indexed":false, "internalType":"uint256", "name":"previousBalance", "type":"uint256" }, { "indexed":false, "internalType":"uint256", "name":"newBalance", "type":"uint256" } ], "name":"DelegateVotesChanged", "type":"event" }, { "anonymous":false, "inputs":[ { "indexed":false, "internalType":"address", "name":"delegator", "type":"address" }, { "indexed":false, "internalType":"address", "name":"delegatee", "type":"address" } ], "name":"GTCDistChanged", "type":"event" }, { "anonymous":false, "inputs":[ { "indexed":false, "internalType":"address", "name":"minter", "type":"address" }, { "indexed":false, "internalType":"address", "name":"newMinter", "type":"address" } ], "name":"MinterChanged", "type":"event" }, { "anonymous":false, "inputs":[ { "indexed":true, "internalType":"address", "name":"from", "type":"address" }, { "indexed":true, "internalType":"address", "name":"to", "type":"address" }, { "indexed":false, "internalType":"uint256", "name":"amount", "type":"uint256" } ], "name":"Transfer", "type":"event" }, { "inputs":[], "name":"DELEGATION_TYPEHASH", "outputs":[ { "internalType":"bytes32", "name":"", "type":"bytes32" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"DOMAIN_TYPEHASH", "outputs":[ { "internalType":"bytes32", "name":"", "type":"bytes32" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"GTCDist", "outputs":[ { "internalType":"address", "name":"", "type":"address" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"PERMIT_TYPEHASH", "outputs":[ { "internalType":"bytes32", "name":"", "type":"bytes32" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"account", "type":"address" }, { "internalType":"address", "name":"spender", "type":"address" } ], "name":"allowance", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"spender", "type":"address" }, { "internalType":"uint256", "name":"rawAmount", "type":"uint256" } ], "name":"approve", "outputs":[ { "internalType":"bool", "name":"", "type":"bool" } ], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"account", "type":"address" } ], "name":"balanceOf", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"", "type":"address" }, { "internalType":"uint32", "name":"", "type":"uint32" } ], "name":"checkpoints", "outputs":[ { "internalType":"uint32", "name":"fromBlock", "type":"uint32" }, { "internalType":"uint96", "name":"votes", "type":"uint96" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"decimals", "outputs":[ { "internalType":"uint8", "name":"", "type":"uint8" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"delegatee", "type":"address" } ], "name":"delegate", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"delegatee", "type":"address" }, { "internalType":"uint256", "name":"nonce", "type":"uint256" }, { "internalType":"uint256", "name":"expiry", "type":"uint256" }, { "internalType":"uint8", "name":"v", "type":"uint8" }, { "internalType":"bytes32", "name":"r", "type":"bytes32" }, { "internalType":"bytes32", "name":"s", "type":"bytes32" } ], "name":"delegateBySig", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"delegator", "type":"address" }, { "internalType":"address", "name":"delegatee", "type":"address" } ], "name":"delegateOnDist", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"", "type":"address" } ], "name":"delegates", "outputs":[ { "internalType":"address", "name":"", "type":"address" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"account", "type":"address" } ], "name":"getCurrentVotes", "outputs":[ { "internalType":"uint96", "name":"", "type":"uint96" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"account", "type":"address" }, { "internalType":"uint256", "name":"blockNumber", "type":"uint256" } ], "name":"getPriorVotes", "outputs":[ { "internalType":"uint96", "name":"", "type":"uint96" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"minimumTimeBetweenMints", "outputs":[ { "internalType":"uint32", "name":"", "type":"uint32" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"dst", "type":"address" }, { "internalType":"uint256", "name":"rawAmount", "type":"uint256" } ], "name":"mint", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[], "name":"mintCap", "outputs":[ { "internalType":"uint8", "name":"", "type":"uint8" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"minter", "outputs":[ { "internalType":"address", "name":"", "type":"address" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"mintingAllowedAfter", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"name", "outputs":[ { "internalType":"string", "name":"", "type":"string" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"", "type":"address" } ], "name":"nonces", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"", "type":"address" } ], "name":"numCheckpoints", "outputs":[ { "internalType":"uint32", "name":"", "type":"uint32" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"owner", "type":"address" }, { "internalType":"address", "name":"spender", "type":"address" }, { "internalType":"uint256", "name":"rawAmount", "type":"uint256" }, { "internalType":"uint256", "name":"deadline", "type":"uint256" }, { "internalType":"uint8", "name":"v", "type":"uint8" }, { "internalType":"bytes32", "name":"r", "type":"bytes32" }, { "internalType":"bytes32", "name":"s", "type":"bytes32" } ], "name":"permit", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"GTCDist_", "type":"address" } ], "name":"setGTCDist", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"minter_", "type":"address" } ], "name":"setMinter", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[], "name":"symbol", "outputs":[ { "internalType":"string", "name":"", "type":"string" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"totalSupply", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"dst", "type":"address" }, { "internalType":"uint256", "name":"rawAmount", "type":"uint256" } ], "name":"transfer", "outputs":[ { "internalType":"bool", "name":"", "type":"bool" } ], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"address", "name":"src", "type":"address" }, { "internalType":"address", "name":"dst", "type":"address" }, { "internalType":"uint256", "name":"rawAmount", "type":"uint256" } ], "name":"transferFrom", "outputs":[ { "internalType":"bool", "name":"", "type":"bool" } ], "stateMutability":"nonpayable", "type":"function" } ]
var gtc_token_abi = [
  {
    constant: true,
    inputs: [],
    name: "name",
    outputs: [
      {
        name: "",
        type: "string",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        name: "_spender",
        type: "address",
      },
      {
        name: "_value",
        type: "uint256",
      },
    ],
    name: "approve",
    outputs: [
      {
        name: "",
        type: "bool",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "totalSupply",
    outputs: [
      {
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        name: "_from",
        type: "address",
      },
      {
        name: "_to",
        type: "address",
      },
      {
        name: "_value",
        type: "uint256",
      },
    ],
    name: "transferFrom",
    outputs: [
      {
        name: "",
        type: "bool",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "decimals",
    outputs: [
      {
        name: "",
        type: "uint8",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [
      {
        name: "_owner",
        type: "address",
      },
    ],
    name: "balanceOf",
    outputs: [
      {
        name: "balance",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "symbol",
    outputs: [
      {
        name: "",
        type: "string",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        name: "_to",
        type: "address",
      },
      {
        name: "_value",
        type: "uint256",
      },
    ],
    name: "transfer",
    outputs: [
      {
        name: "",
        type: "bool",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [
      {
        name: "_owner",
        type: "address",
      },
      {
        name: "_spender",
        type: "address",
      },
    ],
    name: "allowance",
    outputs: [
      {
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    payable: true,
    stateMutability: "payable",
    type: "fallback",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        name: "owner",
        type: "address",
      },
      {
        indexed: true,
        name: "spender",
        type: "address",
      },
      {
        indexed: false,
        name: "value",
        type: "uint256",
      },
    ],
    name: "Approval",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        name: "from",
        type: "address",
      },
      {
        indexed: true,
        name: "to",
        type: "address",
      },
      {
        indexed: false,
        name: "value",
        type: "uint256",
      },
    ],
    name: "Transfer",
    type: "event",
  },
];
const DAIABI = [
  {
    inputs: [
      {
        internalType: "uint256",
        name: "chainId_",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "constructor",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "address",
        name: "src",
        type: "address",
      },
      {
        indexed: true,
        internalType: "address",
        name: "guy",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "Approval",
    type: "event",
  },
  {
    anonymous: true,
    inputs: [
      {
        indexed: true,
        internalType: "bytes4",
        name: "sig",
        type: "bytes4",
      },
      {
        indexed: true,
        internalType: "address",
        name: "usr",
        type: "address",
      },
      {
        indexed: true,
        internalType: "bytes32",
        name: "arg1",
        type: "bytes32",
      },
      {
        indexed: true,
        internalType: "bytes32",
        name: "arg2",
        type: "bytes32",
      },
      {
        indexed: false,
        internalType: "bytes",
        name: "data",
        type: "bytes",
      },
    ],
    name: "LogNote",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "address",
        name: "src",
        type: "address",
      },
      {
        indexed: true,
        internalType: "address",
        name: "dst",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "Transfer",
    type: "event",
  },
  {
    constant: true,
    inputs: [],
    name: "DOMAIN_SEPARATOR",
    outputs: [
      {
        internalType: "bytes32",
        name: "",
        type: "bytes32",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "PERMIT_TYPEHASH",
    outputs: [
      {
        internalType: "bytes32",
        name: "",
        type: "bytes32",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    name: "allowance",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "usr",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "approve",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    name: "balanceOf",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "usr",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "burn",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "decimals",
    outputs: [
      {
        internalType: "uint8",
        name: "",
        type: "uint8",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "guy",
        type: "address",
      },
    ],
    name: "deny",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "usr",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "mint",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "src",
        type: "address",
      },
      {
        internalType: "address",
        name: "dst",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "move",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "name",
    outputs: [
      {
        internalType: "string",
        name: "",
        type: "string",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    name: "nonces",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "holder",
        type: "address",
      },
      {
        internalType: "address",
        name: "spender",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "nonce",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "expiry",
        type: "uint256",
      },
      {
        internalType: "bool",
        name: "allowed",
        type: "bool",
      },
      {
        internalType: "uint8",
        name: "v",
        type: "uint8",
      },
      {
        internalType: "bytes32",
        name: "r",
        type: "bytes32",
      },
      {
        internalType: "bytes32",
        name: "s",
        type: "bytes32",
      },
    ],
    name: "permit",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "usr",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "pull",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "usr",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "push",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "guy",
        type: "address",
      },
    ],
    name: "rely",
    outputs: [],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "symbol",
    outputs: [
      {
        internalType: "string",
        name: "",
        type: "string",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "totalSupply",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "dst",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "transfer",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: false,
    inputs: [
      {
        internalType: "address",
        name: "src",
        type: "address",
      },
      {
        internalType: "address",
        name: "dst",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "wad",
        type: "uint256",
      },
    ],
    name: "transferFrom",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    payable: false,
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    constant: true,
    inputs: [],
    name: "version",
    outputs: [
      {
        internalType: "string",
        name: "",
        type: "string",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  {
    constant: true,
    inputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    name: "wards",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
];
var token_distributor_abi = [ { "inputs":[ { "internalType":"address", "name":"_token", "type":"address" }, { "internalType":"address", "name":"_signer", "type":"address" }, { "internalType":"address", "name":"_timeLock", "type":"address" }, { "internalType":"bytes32", "name":"_merkleRoot", "type":"bytes32" } ], "stateMutability":"nonpayable", "type":"constructor" }, { "anonymous":false, "inputs":[ { "indexed":false, "internalType":"uint256", "name":"user_id", "type":"uint256" }, { "indexed":false, "internalType":"address", "name":"account", "type":"address" }, { "indexed":false, "internalType":"uint256", "name":"amount", "type":"uint256" }, { "indexed":false, "internalType":"bytes32", "name":"leaf", "type":"bytes32" } ], "name":"Claimed", "type":"event" }, { "anonymous":false, "inputs":[ { "indexed":false, "internalType":"uint256", "name":"amount", "type":"uint256" } ], "name":"TransferUnclaimed", "type":"event" }, { "inputs":[], "name":"CONTRACT_ACTIVE", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"uint32", "name":"user_id", "type":"uint32" }, { "internalType":"address", "name":"user_address", "type":"address" }, { "internalType":"uint256", "name":"user_amount", "type":"uint256" }, { "internalType":"address", "name":"delegate_address", "type":"address" }, { "internalType":"bytes32", "name":"eth_signed_message_hash_hex", "type":"bytes32" }, { "internalType":"bytes", "name":"eth_signed_signature_hex", "type":"bytes" }, { "internalType":"bytes32[]", "name":"merkleProof", "type":"bytes32[]" }, { "internalType":"bytes32", "name":"leaf", "type":"bytes32" } ], "name":"claimTokens", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[], "name":"deployTime", "outputs":[ { "internalType":"uint256", "name":"", "type":"uint256" } ], "stateMutability":"view", "type":"function" }, { "inputs":[ { "internalType":"uint256", "name":"index", "type":"uint256" } ], "name":"isClaimed", "outputs":[ { "internalType":"bool", "name":"", "type":"bool" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"merkleRoot", "outputs":[ { "internalType":"bytes32", "name":"", "type":"bytes32" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"signer", "outputs":[ { "internalType":"address", "name":"", "type":"address" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"timeLockContract", "outputs":[ { "internalType":"address", "name":"", "type":"address" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"token", "outputs":[ { "internalType":"address", "name":"", "type":"address" } ], "stateMutability":"view", "type":"function" }, { "inputs":[], "name":"transferUnclaimed", "outputs":[], "stateMutability":"nonpayable", "type":"function" } ]
var governor_alpha_abi = [ {"inputs":[ {"internalType":"address","name":"timelock_","type":"address" }, {"internalType":"address","name":"gtc_","type":"address" } ],"name":"constructor","stateMutability":"nonpayable","type":"constructor" }, {"anonymous":false,"inputs":[ {"indexed":false,"internalType":"uint256","name":"id","type":"uint256" } ],"name":"ProposalCanceled","type":"event" }, {"anonymous":false,"inputs":[ {"indexed":false,"internalType":"uint256","name":"id","type":"uint256" }, {"indexed":false,"internalType":"address","name":"proposer","type":"address" }, {"indexed":false,"internalType":"address[]","name":"targets","type":"address[]" }, {"indexed":false,"internalType":"uint256[]","name":"values","type":"uint256[]" }, {"indexed":false,"internalType":"string[]","name":"signatures","type":"string[]" }, {"indexed":false,"internalType":"bytes[]","name":"calldatas","type":"bytes[]" }, {"indexed":false,"internalType":"uint256","name":"startBlock","type":"uint256" }, {"indexed":false,"internalType":"uint256","name":"endBlock","type":"uint256" }, {"indexed":false,"internalType":"string","name":"description","type":"string" } ],"name":"ProposalCreated","type":"event" }, {"anonymous":false,"inputs":[ {"indexed":false,"internalType":"uint256","name":"id","type":"uint256" } ],"name":"ProposalExecuted","type":"event" }, {"anonymous":false,"inputs":[ {"indexed":false,"internalType":"uint256","name":"id","type":"uint256" }, {"indexed":false,"internalType":"uint256","name":"eta","type":"uint256" } ],"name":"ProposalQueued","type":"event" }, {"anonymous":false,"inputs":[ {"indexed":false,"internalType":"address","name":"voter","type":"address" }, {"indexed":false,"internalType":"uint256","name":"proposalId","type":"uint256" }, {"indexed":false,"internalType":"bool","name":"support","type":"bool" }, {"indexed":false,"internalType":"uint256","name":"votes","type":"uint256" } ],"name":"VoteCast","type":"event" }, {"inputs":[],"name":"BALLOT_TYPEHASH","outputs":[ {"internalType":"bytes32","name":"","type":"bytes32" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"DOMAIN_TYPEHASH","outputs":[ {"internalType":"bytes32","name":"","type":"bytes32" } ],"stateMutability":"view","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" } ],"name":"cancel","outputs":[],"stateMutability":"nonpayable","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" }, {"internalType":"bool","name":"support","type":"bool" } ],"name":"castVote","outputs":[],"stateMutability":"nonpayable","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" }, {"internalType":"bool","name":"support","type":"bool" }, {"internalType":"uint8","name":"v","type":"uint8" }, {"internalType":"bytes32","name":"r","type":"bytes32" }, {"internalType":"bytes32","name":"s","type":"bytes32" } ],"name":"castVoteBySig","outputs":[],"stateMutability":"nonpayable","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" } ],"name":"execute","outputs":[],"stateMutability":"payable","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" } ],"name":"getActions","outputs":[ {"internalType":"address[]","name":"targets","type":"address[]" }, {"internalType":"uint256[]","name":"values","type":"uint256[]" }, {"internalType":"string[]","name":"signatures","type":"string[]" }, {"internalType":"bytes[]","name":"calldatas","type":"bytes[]" } ],"stateMutability":"view","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" }, {"internalType":"address","name":"voter","type":"address" } ],"name":"getReceipt","outputs":[ {"components":[ {"internalType":"bool","name":"hasVoted","type":"bool" }, {"internalType":"bool","name":"support","type":"bool" }, {"internalType":"uint96","name":"votes","type":"uint96" } ],"internalType":"structGovernorAlpha.Receipt","name":"","type":"tuple" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"gtc","outputs":[ {"internalType":"contractGTCInterface","name":"","type":"address" } ],"stateMutability":"view","type":"function" }, {"inputs":[ {"internalType":"address","name":"","type":"address" } ],"name":"latestProposalIds","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"name","outputs":[ {"internalType":"string","name":"","type":"string" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"proposalCount","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"proposalMaxOperations","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"pure","type":"function" }, {"inputs":[],"name":"proposalThreshold","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"pure","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"name":"proposals","outputs":[ {"internalType":"uint256","name":"id","type":"uint256" }, {"internalType":"address","name":"proposer","type":"address" }, {"internalType":"uint256","name":"eta","type":"uint256" }, {"internalType":"uint256","name":"startBlock","type":"uint256" }, {"internalType":"uint256","name":"endBlock","type":"uint256" }, {"internalType":"uint256","name":"forVotes","type":"uint256" }, {"internalType":"uint256","name":"againstVotes","type":"uint256" }, {"internalType":"bool","name":"canceled","type":"bool" }, {"internalType":"bool","name":"executed","type":"bool" } ],"stateMutability":"view","type":"function" }, {"inputs":[ {"internalType":"address[]","name":"targets","type":"address[]" }, {"internalType":"uint256[]","name":"values","type":"uint256[]" }, {"internalType":"string[]","name":"signatures","type":"string[]" }, {"internalType":"bytes[]","name":"calldatas","type":"bytes[]" }, {"internalType":"string","name":"description","type":"string" } ],"name":"propose","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"nonpayable","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" } ],"name":"queue","outputs":[],"stateMutability":"nonpayable","type":"function" }, {"inputs":[],"name":"quorumVotes","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"pure","type":"function" }, {"inputs":[ {"internalType":"uint256","name":"proposalId","type":"uint256" } ],"name":"state","outputs":[ {"internalType":"enumGovernorAlpha.ProposalState","name":"","type":"uint8" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"timelock","outputs":[ {"internalType":"contractTimelockInterface","name":"","type":"address" } ],"stateMutability":"view","type":"function" }, {"inputs":[],"name":"votingDelay","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"pure","type":"function" }, {"inputs":[],"name":"votingPeriod","outputs":[ {"internalType":"uint256","name":"","type":"uint256" } ],"stateMutability":"pure","type":"function" } ]

var bounty_address = function() {
  if (document.web3network === null) {
    // default to mainnet if web3network isn't found in time
    document.web3network = 'mainnet';
  }
  switch (document.web3network) {
    case 'mainnet':
      return '0x2af47a65da8cd66729b4209c22017d6a5c2d2400';
    case 'ropsten':
      throw 'this network is not supported in bounty_address() for gitcoin';
    case 'kovan':
      throw 'this network is not supported in bounty_address() for gitcoin';
    case 'rinkeby':
      return '0xf209d2b723b6417cbf04c07e733bee776105a073';
    case 'custom network':
      // This only works if you deploy the Standard Bounties contract locally
      // Set the testrpc address to the address below in in the truffle.js file.
      // In the Standard Bounties repo, `truffle deploy --network testrpc`
      return '0x9ee228365ebc1da6a5d025fdf0939edf2bea21da';
  }
};

var kudos_address = function() {
  if (document.web3network === null) {
    // default to mainnet if web3network isn't found in time
    document.web3network = 'mainnet';
  }
  switch (document.web3network) {
    case 'mainnet':
      return '0x2aea4add166ebf38b63d09a75de1a7b94aa24163';
    case 'ropsten':
      return '0xcd520707fc68d153283d518b29ada466f9091ea8';
    case 'xdai':
      return '0x74e596525C63393f42C76987b6A66F4e52733efa';
    case 'kovan':
      throw 'this network is not supported for kudos';
    case 'rinkeby':
      return '0x4077ae95eec529d924571d00e81ecde104601ae8';
    case 'custom network':
      // This only works if you deploy the Standard Bounties contract locally
      // Set the testrpc address to the address below in in the truffle.js file.
      // In the Standard Bounties repo, `truffle deploy --network testrpc`
      return '0xe7bed272ee374e8116049d0a49737bdda86325b6';
  }
};

/**
 * Returns etherscan link of transaction /
 * @param {string} id
 * @param {string} network
 * @param {enum} type tx | address
 */
var get_etherscan_url = function(id, network, type = 'tx') {
  let _network = network ? network : document.web3network;
  switch (_network) {
    case 'mainnet':
      return 'https://etherscan.io/' + type + '/' + id;
    case 'ropsten':
      return 'https://ropsten.etherscan.io/' + type + '/' + id;
    case 'kovan':
      return 'https://kovan.etherscan.io/'  + type + '/' + id;
    case 'rinkeby':
      return 'https://rinkeby.etherscan.io/' + type + '/' + id;
    case 'custom network':
      return 'https://localhost/' + type + '/' + id;
    default:
      return 'https://etherscan.io/' + type + '/' + id;
  }
};

/**
 * Returns zkScan link of an transaction or address /
 * @param {string} id
 * @param {string} network zkScan is on mainnet, rinkeby, and ropsten
 * @param {enum} type accounts | transactions
 */
var get_zkscan_url = function(id, network, type = 'transactions') {
  let _network = network ? network : document.web3network;
  switch (_network) {
    case 'mainnet':
      return 'https://zkscan.io/explorer/' + type + '/' + id;
    case 'ropsten':
      return 'https://ropsten.zkscan.io/explorer/' + type + '/' + id;
    case 'rinkeby':
      return 'https://rinkeby.zkscan.io/explorer/' + type + '/' + id;
    case 'custom network':
      return 'https://localhost/explorer/' + type + '/' + id;
    default:
      return 'https://zkscan.io/explorer/' + type + '/' + id;
  }
};

var gtc_address = function() {
  if (document.web3network === null) {
    // default to mainnet if web3network isn't found in time
    document.web3network = 'mainnet';
  }
  switch (document.web3network) {
    case 'mainnet':
      return '0x5592ec0cfb4dbc12d3ab100b257153436a1f0fea';
    case 'ropsten':
      throw 'this network is not supported in GTC for gitcoin';
    case 'kovan':
      throw 'this network is not supported in GTC for gitcoin';
    case 'rinkeby':
      throw '0x5592ec0cfb4dbc12d3ab100b257153436a1f0fea';
  }
};

var token_distributor_address = function() {
  if (document.web3network === null) {
    // default to mainnet if web3network isn't found in time
    document.web3network = 'mainnet';
  }
  switch (document.web3network) {
    case 'mainnet':
      return '0xDE3e5a990bCE7fC60a6f017e7c4a95fc4939299E';
    case 'ropsten':
      throw 'this network is not supported for TokenDistributor gitcoin';
    case 'kovan':
      throw 'this network is not supported for TokenDistributor gitcoin';
    case 'rinkeby':
      throw 'this network is not supported for TokenDistributor gitcoin';
  }
};

var governor_alpha_address = function() {
  if (document.web3network === null) {
    // default to mainnet if web3network isn't found in time
    document.web3network = 'mainnet';
  }
  switch (document.web3network) {
    case 'mainnet':
      return '0xDbD27635A534A3d3169Ef0498beB56Fb9c937489';
    case 'ropsten':
      throw 'this network is not supported in GTC for gitcoin';
    case 'kovan':
      throw 'this network is not supported in GTC for gitcoin';
    case 'rinkeby':
      throw 'this network is not supported in GTC for gitcoin';
  }
};

var erc20_approve_gas = 560000;
var max_gas_for_erc20_bounty_post = 517849;
var gasLimitMultiplier = 4;
var gasMultiplier = 1.3;
var defaultGasPrice = Math.pow(10, 9) * 5; // 5 gwei
var weiPerEther = Math.pow(10, 18);
