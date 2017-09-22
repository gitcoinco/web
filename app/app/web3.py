from web3 import Web3, IPCProvider, EthereumTesterProvider, RPCProvider

web3 = mainnnet = Web3(IPCProvider())
testnet = Web3(IPCProvider(ipc_path='/root/.ethereum/testnet/geth.ipc',testnet=True))
devnet = Web3(IPCProvider(ipc_path='/tmp/ethereum_dev_mode/geth.ipc',testnet=True))
customnet = Web3(IPCProvider(ipc_path='/root/owockinet/geth.ipc',testnet=True))
infura = Web3(RPCProvider(host='ropsten.infura.io',port=443,path='/',ssl=True))
tester = Web3(EthereumTesterProvider())

#accounts
accounts = tester.eth.accounts
web3.eth.getBalance('0xd3cda913deb6f67967b99d67acdfa1712c293601')

web3.personal.importRawKey(private_key, passphrase)
web3.personal.newAccount(self, password=None)


#blocks 
web3.eth.getBlockTransactionCount(46147)
web3.eth.getBlock(2000000)
web3.eth.getTransactionReceipt('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060')  # not yet mined
web3.eth.sendTransaction({'to': '0xd3cda913deb6f67967b99d67acdfa1712c293601', 'from': web3.eth.coinbase, 'value': 12345})

import rlp
from ethereum.transactions import Transaction
tx = Transaction(
    nonce=web3.eth.getTransactionCount(web3.eth.coinbase),
    gasprice=web3.eth.gasPrice,
    startgas=100000,
    to='0xd3cda913deb6f67967b99d67acdfa1712c293601',
    value=12345,
    data='',
)
the_private_key_for_the_from_account = 'foo bar'
tx.sign(the_private_key_for_the_from_account)
raw_tx = rlp.encode(tx)
raw_tx_hex = web3.toHex(raw_tx)
web3.eth.sendRawTransaction(raw_tx_hex)
'0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331'


#contracts
token_contract = my_token_contract = my_contract = tester.eth.contract(address=None, contract_name=None, ContractFactoryClass=Contract, **contract_factory_kwargs)
# http://web3py.readthedocs.io/en/latest/contracts.html
token_contract.transact().transfer(accounts[1], 12345)
token_contract.call({'from': web3.eth.coinbase}).myBalance()
my_contract.call().multiply7(3)

#filters
#http://web3py.readthedocs.io/en/latest/web3.eth.html#filters
#past events
transfer_filter = my_token_contract.pastEvents('Transfer', {'filters': {'_from': '0xdc3a9db694bcdd55ebae4a89b22ac6d12b3f0c24'}})
#future events
transfer_filter = my_token_contract.on('Transfer', {'filters': {'_from': '0xdc3a9db694bcdd55ebae4a89b22ac6d12b3f0c24'}})
transfer_filter.get()
transfer_filter.watch(my_callback)
