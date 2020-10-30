var binance_utils = {};

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
