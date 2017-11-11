'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
from django.conf import settings
import json
from web3 import Web3
from web3.providers.rpc import KeepAliveRPCProvider, HTTPProvider


def get_network_details(network):
    bounty_contract_address = None
    if network == 'mainnet':
        bounty_contract_address = '0x4e1799e6e54d848394b0b90593e789e939a9f801'
        infura_host = 'mainnet.infura.io'
        custom_geth_details = (settings.CUSTOM_MAINNET_GETH_HOST, settings.CUSTOM_MAINNET_GETH_PORT)
        is_testnet = False
    elif network == 'ropsten':
        bounty_contract_address = '0x3102118ba636942c82d1a6efa2e7d069dc2d14bd'
        infura_host = 'ropsten.infura.io'
        custom_geth_details = (settings.CUSTOM_RINKEBY_GETH_HOST, settings.CUSTOM_RINKEBY_GETH_PORT)
        is_testnet = True
    elif network == 'kovan':
        raise
    elif network == 'rinkeby':
        raise
    elif network == 'testrpc':
        bounty_contract_address = settings.TESRPC_CONTRACT_ADDRESS
        infura_host = 'na'
        custom_geth_details = (settings.CUSTOM_TESTRPC_GETH_HOST, settings.CUSTOM_TESTRPC_GETH_PORT)
        is_testnet = True
    else:
        raise

    return (bounty_contract_address, infura_host, custom_geth_details, is_testnet)


def getWeb3(network, prefer_provider='default'):

    bounty_contract_address, infura_host, custom_geth_details, is_testnet = get_network_details(network)
    custom_geth_host = custom_geth_details[0]
    custom_geth_port = custom_geth_details[1]

    def rpc_web3():
        return Web3(KeepAliveRPCProvider(host=custom_geth_host, port=custom_geth_port))

    def http_web3():
        # return Web3(HTTPProvider('https://'+infura_host+'/'+settings.INFURA_KEY))
        return Web3(Web3.RPCProvider(
            host=infura_host,
            path=settings.INFURA_KEY,
            port='443',
            ssl=1))

    # no infura for testrpc!
    if network == 'testrpc':
        return rpc_web3()

    # return diff provider based upon input
    if prefer_provider == 'infura':
        return http_web3()
    elif prefer_provider == 'default':
        return http_web3()
    elif prefer_provider == 'custom':
        return rpc_web3()
    else:
        raise


# http://web3py.readthedocs.io/en/latest/contracts.html
def getBountyContract(web3, bounty_contract_address):
    abi_str = '[{"inputs": [{"type": "uint256", "name": ""}], "constant": true, "name": "bounty_indices", "outputs": [{"type": "bytes32", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "bountiesbyrepo", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "str"}], "constant": false, "name": "normalizeIssueURL", "outputs": [{"type": "string", "name": "result"}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "str"}], "constant": false, "name": "getRepoURL", "outputs": [{"type": "string", "name": "result"}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}, {"type": "uint256", "name": "_amount"}, {"type": "address", "name": "_tokenAddress"}, {"type": "uint256", "name": "_expirationTimeDelta"}, {"type": "string", "name": "_metaData"}], "constant": false, "name": "postBounty", "outputs": [{"type": "bool", "name": ""}], "payable": true, "type": "function"}, {"inputs": [], "constant": true, "name": "numBounties", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_repoURL"}], "constant": false, "name": "getNumberBounties", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}, {"type": "string", "name": "_claimee_metaData"}], "constant": false, "name": "claimBounty", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "clawbackExpiredBounty", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "rejectBountyClaim", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "bountydetails", "outputs": [{"type": "uint256", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "bool", "name": ""}, {"type": "bool", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": "index"}], "constant": false, "name": "_bountydetails", "outputs": [{"type": "uint256", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "bool", "name": ""}, {"type": "bool", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}, {"type": "uint256", "name": ""}, {"type": "string", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "Bounties", "outputs": [{"type": "uint256", "name": "amount"}, {"type": "address", "name": "bountyOwner"}, {"type": "address", "name": "claimee"}, {"type": "string", "name": "claimee_metaData"}, {"type": "uint256", "name": "creationTime"}, {"type": "uint256", "name": "expirationTime"}, {"type": "bool", "name": "initialized"}, {"type": "string", "name": "issueURL"}, {"type": "string", "name": "metaData"}, {"type": "bool", "name": "open"}, {"type": "address", "name": "tokenAddress"}], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "_issueURL"}], "constant": false, "name": "approveBountyClaim", "outputs": [], "payable": false, "type": "function"}, {"inputs": [{"type": "string", "name": "str"}], "constant": false, "name": "strToMappingIndex", "outputs": [{"type": "bytes32", "name": "result"}], "payable": false, "type": "function"}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}, {"indexed": false, "type": "uint256", "name": "amount"}], "type": "event", "name": "bountyPosted", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyClaimed", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyExpired", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "address", "name": "payee"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyClaimApproved", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "string", "name": "issueURL"}], "type": "event", "name": "bountyClaimRejected", "anonymous": false}]';
    bounty_abi = json.loads(abi_str);
    getBountyContract = web3.eth.contract(abi=bounty_abi, address=bounty_contract_address);
    return getBountyContract