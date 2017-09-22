from web3 import Web3, IPCProvider
from web3.providers.rpc import RPCProvider

print("****************************************")
try:
    testnet = Web3(IPCProvider(ipc_path='/root/.ethereum/testnet/geth.ipc',testnet=True))
    syncing = testnet.eth.syncing
    if not syncing:
        pct = 100
    else:
        pct = round(syncing['currentBlock'] / syncing['highestBlock'],2) * 100
    print("testnet : {}%".format(pct))
    print("Details => {}".format(syncing))
except Exception as e:
    print(e)
    
print("****************************************")
try:
    mainnnet = Web3(RPCProvider(host='34.209.54.67',port=30303))
    syncing = mainnnet.eth.syncing
    if not syncing:
        pct = 100
    else:
        pct = round( syncing['currentBlock'] / syncing['highestBlock'],2) * 100
    print("mainnnet : {}%".format(pct))
    print("Details => {}".format(syncing))
except Exception as e:
    print(e)

print("****************************************")
try:
    mainnnet = Web3(IPCProvider(ipc_path='/root/.ethereum/geth.ipc',testnet=True))
    syncing = mainnnet.eth.syncing
    if not syncing:
        pct = 100
    else:
        pct = round(syncing['currentBlock'] / syncing['highestBlock'],2) * 100
    print("mainnnet : {}%".format(pct))
    print("Details => {}".format(syncing))
except Exception as e:
    print(e)
    