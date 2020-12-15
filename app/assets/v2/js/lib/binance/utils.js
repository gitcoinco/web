var binance_utils = {};

binance_utils.getChainVerbose = chainId => {
  switch (chainId) {
    case 'Binance-Chain-Tigris':
      return { name: 'Binance Chain Network', addressType: 'bbc-mainnet' };
    case 'Binance-Chain-Ganges':
      return { name: 'Binance Chain Test Network', addressType: 'bbc-testnet' };
    case '0x38':
      return { name: 'Binance Smart Chain Network', addressType: 'eth' };
    case '0x61':
      return { name: 'Binance Smart Chain Test Network', addressType: 'eth' };
  }
}


/**
 * Returns wallet's balance on the connected binance network
 * @param {String} address
 */
binance_utils.getAddressBalance = async address => {
  const isConnected = await BinanceChain.isConnected();

  if (!isConnected || !address)
    return;

  data = {
    method: 'eth_getBalance',
    params: [address, 'latest']
  };
  
  const result = await BinanceChain.request(data);
  
  // convert hex balance to integer and account for decimal points
  const bnbBalance = BigInt(result).toString(10) * 10 ** -18;

  return Promise.resolve(bnbBalance.toFixed(4));
};


/**
 * Get accounts connected in extension
 */
binance_utils.getExtensionConnectedAccounts = async () => {
  const isConnected = await BinanceChain.isConnected();

  if (!isConnected)
    return;

  const accounts = await BinanceChain.requestAccounts();

  return Promise.resolve(accounts);
};


/**
 * Sign and transfer token to another address via extension and returns txn hash
 * @param {Number} amount
 * @param {String} to_address
 * @param {String} from_address : optional, if not passed takes account first account from getExtensionConnectedAccounts
 */
binance_utils.transferViaExtension = async (amount, to_address, from_address) => {

  return new Promise(async(resolve, reject) => {

    const isConnected = await BinanceChain.isConnected();

    if (!isConnected) {
      reject(`transferViaExtension: binance hasn't connected to the network ${binance_utils.getChainVerbose(BinanceChain.chainId).name}`);
    } else if (!amount) {
      reject('transferViaExtension: missing param amount');
    } else if (!to_address) {
      reject('transferViaExtension: missing param to_address');
    }

    const chainVerbose = binance_utils.getChainVerbose(BinanceChain.chainId);

    if (!from_address) {
      const accounts = await binance_utils.getExtensionConnectedAccounts();
      from_address = accounts && accounts[0]['addresses'].find(address => address.type === chainVerbose.addressType).address;
    }
  
    if (!from_address) {
      reject('transferViaExtension: missing param from_address');
    }
  
    const account_balance = await binance_utils.getAddressBalance(from_address);

    if (Number(account_balance) < amount) {
      reject(`transferViaExtension: insufficent balance in address ${from_address}`);
    }

    if (chainVerbose.addressType === 'eth') {
      const params = [
        {
          from: from_address,
          to: to_address,
          value: '0x' + amount.toString(16) // convert amount to hex
        },
      ];

      BinanceChain
        .request({
          method: 'eth_sendTransaction',
          params
        })
        .then(txHash => {
          resolve(txHash);
        })
        .catch(error => {
          reject('transferViaExtension: something went wrong' + error);
        });
    }
  });
};


/* EVENTS */
BinanceChain.on('connect', info => {
  console.log(`connected to ${binance_utils.getChainVerbose(info.chainId).name}!`);
});

BinanceChain.on('chainChanged', chainId => {
  console.log(`connected to ${binance_utils.getChainVerbose(chainId).name}!`);
  window.location.reload(); // reload page when chain changes
});
