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

  if (typeof BinanceChain === "undefined")
    throw new Error('Please ensure your Binance Chain Extension wallet is installed and enabled');

  const isConnected = await BinanceChain.isConnected();

  if (!isConnected || !address)
    return;

  const result = await jsonRpcRequest('eth_getBalance', [address, 'latest']);

  // convert hex balance to integer
  const bnbBalance = BigInt(result).toString(10);

  return Promise.resolve(bnbBalance);
};

/**
 * Returns wallet's BEP20 token balance on the connected binance network
 * @param {String} address
 * @param {String} tokenContractAddress
 */
binance_utils.getAddressTokenBalance = async (address, tokenContractAddress) => {

  if (typeof BinanceChain === "undefined")
    throw new Error('Please ensure your Binance Chain Extension wallet is installed and enabled');

  const isConnected = await BinanceChain.isConnected();

  if (!isConnected || !address || !tokenContractAddress)
    return;

  const method_id = "0x70a08231";
  address = address.substr(2).padStart(64, '0'); // remove 0x and pad with zeroes

  const params = [
    {
      to: tokenContractAddress,
      data: method_id + address
    },
    'latest'
  ]
  const result = await jsonRpcRequest('eth_call', params);

  // convert hex balance to integer
  const tokenBalance = BigInt(result).toString(10);

  return Promise.resolve(tokenBalance);
};


/**
 * Get accounts connected in extension
 */
binance_utils.getExtensionConnectedAccounts = async () => {

  if (typeof BinanceChain === "undefined")
    throw new Error('Please ensure your Binance Chain Extension wallet is installed and enabled');

  const isConnected = await BinanceChain.isConnected();

  if (!isConnected)
    return;

  const accounts = await BinanceChain.requestAccounts();

  return Promise.resolve(accounts);
};


/**
 * Get selected account connected in extension
 */
binance_utils.getSelectedAccount = async () => {

  return new Promise(async (resolve, reject) => {

    if (typeof BinanceChain === "undefined") {
      reject('Please ensure you are connected to your wallet via the <a target="_blank" class="underline" rel="noopener noreferrer" href="https://chrome.google.com/webstore/detail/binance-wallet/fhbohimaelbohpjbbldcngcnapndodjp">Binance Wallet extension</a>');
    }

    const chainVerbose = binance_utils.getChainVerbose(BinanceChain.chainId);
    const accounts = await binance_utils.getExtensionConnectedAccounts();
    address = accounts && accounts[0]['addresses'].find(address => address.type === chainVerbose.addressType).address;

    resolve(address)
  });
}


/**
 * Sign and transfer token to another address via extension and returns txn hash
 * @param {Number} amount : in wei
 * @param {String} to_address
 * @param {String} token_name
 * @param {String} from_address : optional, if not passed takes account first account from getExtensionConnectedAccounts
 */
binance_utils.transferViaExtension = async (amount, to_address, from_address, token_name) => {

  return new Promise(async (resolve, reject) => {

    if (typeof BinanceChain === "undefined") {
      reject('Please ensure you are connected to your wallet via the <a target="_blank" class="underline" rel="noopener noreferrer" href="https://chrome.google.com/webstore/detail/binance-wallet/fhbohimaelbohpjbbldcngcnapndodjp">Binance Wallet extension</a>');
    }

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
      from_address = await binance_utils.getSelectedAccount();
    }

    if (!from_address) {
      reject('transferViaExtension: missing param from_address');
    }

    if (!token_name) {
      token_name = 'BNB';
    }

    if (token_name === 'BNB') {

      const account_balance = await binance_utils.getAddressBalance(from_address);

      if (Number(account_balance) < amount) {
        reject(`transferViaExtension: Insufficient balance in address ${from_address}`);
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

      const busd_contract_address = '0xe9e7cea3dedca5984780bafc599bd69add087d56'

      const account_balance = await binance_utils.getAddressTokenBalance(from_address, busd_contract_address);

      if (Number(account_balance) < amount ) {
        reject(`transferViaExtension: Insufficient balance in address ${from_address}`);
      }

      if (chainVerbose.addressType === 'eth') {
        try {
          const method_id = "0xa9059cbb";
          amount = amount.toString(16).padStart(64, '0'); // convert to hex and pad with zeroes
          to_address = to_address.substr(2).padStart(64, '0'); // remove 0x and pad with zeroes

          const params = [
            {
              from: from_address,
              to: busd_contract_address,
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
// BinanceChain.on('connect', info => {
//   console.log(`connected to ${binance_utils.getChainVerbose(info.chainId).name}!`);
// });

// BinanceChain.on('chainChanged', chainId => {
//   console.log(`connected to ${binance_utils.getChainVerbose(chainId).name}!`);
//   window.location.reload(); // reload page when chain changes
// });
