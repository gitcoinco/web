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

async function jsonRpcRequest(method, params) {
  return new Promise(async (resolve, reject) => {
    BinanceChain
      .request({ method, params })
      .then(result => {
        resolve(result);
      })
      .catch(error => {
        reject(error);
      });
  });
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
 * Returns wallet's BEP20 token balance on the connected binance network
 * @param {String} address
 * @param {String} tokenContractAddress
 */
binance_utils.getAddressTokenBalance = async (address, tokenContractAddress) => {
  const isConnected = await BinanceChain.isConnected();

  if (!isConnected || !address || !tokenContractAddress)
    return;

  const methodSignature = await jsonRpcRequest(
    'web3_sha3',
    ['balanceOf(address)']
  );
  const method_id = methodSignature.substr(0, 10);
  const address = address.substr(2).padStart(64, '0'); // remove 0x and pad with zeroes

  const params = [
    {
      to: tokenContractAddress,
      data: method_id + address
    },
    'latest'
  ]
  const result = await jsonRpcRequest('eth_call', params);

  // convert hex balance to integer and account for decimal points
  const tokenBalance = BigInt(result).toString(10) * 10 ** -18;

  return Promise.resolve(tokenBalance.toFixed(4));
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
 * @param {String} token_name
 * @param {String} from_address : optional, if not passed takes account first account from getExtensionConnectedAccounts
 */
binance_utils.transferViaExtension = async (amount, to_address, from_address, token_name) => {

  return new Promise(async (resolve, reject) => {

    const isConnected = await BinanceChain.isConnected();

    if (!isConnected) {
      reject(`transferViaExtension: binance hasn't connected to the network ${binance_utils.getChainVerbose(BinanceChain.chainId).name}`);
    } else if (!amount) {
      reject('transferViaExtension: missing param amount');
    } else if (!to_address) {
      reject('transferViaExtension: missing param to_address');
    }

    if (!token_name) {
      token_name = 'BNB';
    }

    const chainVerbose = binance_utils.getChainVerbose(BinanceChain.chainId);

    if (!from_address) {
      const accounts = await binance_utils.getExtensionConnectedAccounts();
      from_address = accounts && accounts[0]['addresses'].find(address => address.type === chainVerbose.addressType).address;
    }

    if (!from_address) {
      reject('transferViaExtension: missing param from_address');
    }

    if (token_name === 'BNB') {

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

        try {
          const txHash = await jsonRpcRequest('eth_sendTransaction', params)
          resolve(txHash)
        } catch (error) {
          reject('transferViaExtension: something went wrong' + error);
        }
      }

    } else if (token_name === 'BUSD') {

      const account_balance = await binance_utils.getAddressTokenBalance(from_address);

      if (Number(account_balance) < amount) {
        reject(`transferViaExtension: insufficent balance in address ${from_address}`);
      }

      if (chainVerbose.addressType === 'eth') {
        try {
          const methodSignature = await jsonRpcRequest(
            'web3_sha3',
            ['transfer(address, uint256)']
          );
          const method_id = methodSignature.substr(0, 10);
          const amount = BigInt(amount * 10 ** 18).toString(16).padStart(64, '0'); // convert to hex and pad with zeroes
          const to_address = to_address.substr(2).padStart(64, '0'); // remove 0x and pad with zeroes

          const params = [
            {
              from: from_address,
              to: '0xe9e7cea3dedca5984780bafc599bd69add087d56', // BUSD token contract address
              data: method_id + to_address + amount
            },
          ]
          const txHash = await jsonRpcRequest('eth_sendTransaction', params);

          resolve(txHash);
        } catch (error) {
          reject('transferViaExtension: something went wrong' + error);
        }
      }
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
