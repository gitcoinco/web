var token_abi = [{"inputs": [], "constant": true, "name": "mintingFinished", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "name", "outputs": [{"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_spender"}, {"type": "uint256", "name": "_value"}], "constant": false, "name": "approve", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "totalSupply", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_from"}, {"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "name": "transferFrom", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "decimals", "outputs": [{"type": "uint8", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_to"}, {"type": "uint256", "name": "_amount"}], "constant": false, "name": "mint", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "version", "outputs": [{"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}], "constant": true, "name": "balanceOf", "outputs": [{"type": "uint256", "name": "balance"}], "payable": false, "type": "function"}, {"inputs": [], "constant": false, "name": "finishMinting", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "owner", "outputs": [{"type": "address", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "symbol", "outputs": [{"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "name": "transfer", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}, {"type": "address", "name": "_spender"}], "constant": true, "name": "allowance", "outputs": [{"type": "uint256", "name": "remaining"}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "newOwner"}], "constant": false, "name": "transferOwnership", "outputs": [], "payable": false, "type": "function"}, {"payable": false, "type": "fallback"}, {"inputs": [{"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "amount"}], "type": "event", "name": "Mint", "anonymous": false}, {"inputs": [], "type": "event", "name": "MintFinished", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer", "anonymous": false}];
var bounty_abi = [{"inputs": [{"type": "uint256", "name": ""}], "constant": true, "name": "bounty_indices", "outputs": [{"type": "bytes32", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "bountiesbyrepo", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "str"}], "constant": false, "name": "normalizeIssueURL", "outputs": [{"type": "string", "name": "result"}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "str"}], "constant": false, "name": "getRepoURL", "outputs": [{"type": "string", "name": "result"}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}, {"type": "uint256", "name": "_amount"}, {"type": "address", "name": "_tokenAddress"}, {"type": "uint256", "name": "_expirationTimeDelta"}, {"type": "string", "name": "_metaData"}], "constant": false, "name": "postBounty", "outputs": [{"type": "bool", "name": ""}], "payable": true, "type": "function"}, {"inputs": [], "constant": true, "name": "numBounties", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_repoURL"}], "constant": false, "name": "getNumberBounties", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}, {"type": "string", "name": "_claimee_metaData"}], "constant": false, "name": "claimBounty", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "clawbackExpiredBounty", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "rejectBountyClaim", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "bountydetails", "outputs": [{"type": "uint256", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "bool", "name": ""}, {"type": "bool", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": "index"}], "constant": false, "name": "_bountydetails", "outputs": [{"type": "uint256", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "bool", "name": ""}, {"type": "bool", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "Bounties", "outputs": [{"type": "uint256", "name": "amount"}, {"type": "address", "name": "bountyOwner"}, {"type": "address", "name": "claimee"}, {"type": "string", "name": "claimee_metaData"}, {"type": "uint256", "name": "creationTime"}, {"type": "uint256", "name": "expirationTime"}, {"type": "bool", "name": "initialized"}, {"type": "string", "name": "issueURL"}, {"type": "string", "name": "metaData"}, {"type": "bool", "name": "open"}, {"type": "address", "name": "tokenAddress"}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "approveBountyClaim", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "str"}], "constant": false, "name": "strToMappingIndex", "outputs": [{"type": "bytes32", "name": "result"}], "payable": false, "type": "function"}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}, {"indexed": false, "type": "uint256", "name": "amount"}], "type": "event", "name": "bountyPosted", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyClaimed", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyExpired", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "address", "name": "payee"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyClaimApproved", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyClaimRejected", "anonymous": false}];


var bounty_address = function (){
    switch(document.web3network){
        case "mainnet":
            return '0xc14c22f07bc8aeda9fd87c7bd579169fd6bf01b5';
        break;
        case "ropsten":
            return '0x3102118ba636942c82d1a6efa2e7d069dc2d14bd';
        break;
        case "kovan":
            throw "not supported";
        break;
        case "rinkeby":
            throw "not supported";
        break;
        case "custom network":
            return '0x0ed0c2a859e9e576cdff840c51d29b6f8a405bdd';
        break;
    }
}

var etherscan_tx_url = function (txid){
    switch(document.web3network){
        case "mainnet":
            return 'https://etherscan.io/tx/' + txid;
        break;
        case "ropsten":
            return 'https://ropsten.etherscan.io/tx/' + txid;
        break;
        case "kovan":
            return 'https://kovan.etherscan.io/tx/' + txid;
        break;
        case "rinkeby":
            return 'https://rinkeby.etherscan.io/tx/' + txid;
        break;
        case "custom network":
            return 'https://localhost/tx/' + txid;
        break;
        default:
            return 'https://etherscan.io/tx/' + txid;
        break;
    }
}

var erc20_approve_gas = 560000;
var max_gas_for_erc20_bounty_post = 517849;
var gasLimitMultiplier = 4;
var gasMultiplier = 1.3;
var defaultGasPrice = 10**9 * 9; //9 gwei
var weiPerEther = 10**18;
