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
  const isConnected = await BinanceChain.isConnected()

  if (!isConnected || !address)
    return;

  data = {
    method: 'eth_getBalance',
    params: [address, 'latest']
  };
  
  const result = await BinanceChain.request(data);
  
  // convert hex balance to integer and account for decimal points
  const bnbBalance = BigInt(result).toString(10) * Math.pow(10, -18);

  return Promise.resolve(bnbBalance.toFixed(4));
};

/**
 * Get accounts connected in extension
 */
binance_utils.getExtensionConnectedAccounts = async () => {
  const isConnected = await BinanceChain.isConnected()

  if (!isConnected)
    return;

  const accounts = await BinanceChain.requestAccounts();

  return Promise.resolve(accounts);
};


/* EVENTS */
BinanceChain.on('connect', info => {
  console.log(`connected to ${binance_utils.getChainVerbose(info.chainId).name}!`);
});

BinanceChain.on('chainChanged', chainId => {
  console.log(`connected to ${binance_utils.getChainVerbose(chainId).name}!`);
  window.location.reload(); // reload page when chain changes
});
