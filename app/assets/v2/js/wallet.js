const Web3Modal = window.Web3Modal.default;
const WalletConnectProvider = window.WalletConnectProvider.default;
const eventWalletReady = new Event('walletReady', {bubbles: true});
const eventWalletDisconnect = new Event('walletDisconnect', {bubbles: true});
const eventDataWalletReady = new Event('dataWalletReady', {bubbles: true});

if (!Object.hasOwnProperty.call(window, 'web3')) {
  window.web3 = null;
}
let web3Modal;
let provider;
let selectedAccount;
let balance;
let chainId;
let networkId;
let networkName;
let chainName;
let humanFriendlyBalance;

if (window.ethereum) {
  window.ethereum.autoRefreshOnNetworkChange = false;
}

function initWallet() {
  // Determine if we're on prod or not
  const url = new URL(document.location.href);
  const isProd = url.host == 'gitcoin.co' && url.protocol == 'https:';
  const formaticKey = isProd ? document.contxt['fortmatic_live_key'] : document.contxt['fortmatic_test_key'];
  const providerOptions = {
    fortmatic: {
      'package': Fortmatic,
      options: {
        key: formaticKey
      }
    },
    walletconnect: {
      'package': WalletConnectProvider,
      options: {
        infuraId: '1e0a90928efe4bb78bb1eeceb8aacc27'
      }
    },
    portis: {
      'package': Portis,
      options: {
        id: 'b2345081-a47e-413a-941f-33fd645d39b3',
        network: 'mainnet'
      }
    }
  };
  const network = isProd ? 'mainnet' : 'rinkeby';

  web3Modal = new Web3Modal({
    network,
    cacheProvider: true,
    providerOptions
  });
  document.dispatchEvent(eventWalletReady);
}

function walletStateChanges() {
  if (typeof load_tokens !== 'undefined' && typeof tokens !== 'undefined') {
    load_tokens();
  }
}

const needWalletConnection = async() => {
  window.addEventListener('walletReady', async function(e) {
    if (!web3Modal || !web3Modal.cachedProvider) {
      return await onConnect().then(console.log);
    } else if (web3Modal.cachedProvider === 'injected' && window.Web3Modal.getInjectedProviderName() === 'MetaMask') {
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });

      if (!accounts.length) {
        return await onConnect().then(console.log);
      }

    }
  }, false);
};

async function fetchAccountData(provider) {

  // Get a Web3 instance for the wallet
  // web3 = new Web3(provider);
  web3 = Web3 ? new Web3(provider || 'ws://localhost:8546') : null;

  console.log('Web3 instance is', web3);

  // Get connected chain id from Ethereum node
  if (web3.eth.currentProvider) {
    chainId = await web3.eth.currentProvider.chainId;
  } else {
    chainId = await web3.eth.givenProvider.chainId;
  }
  await web3.eth.net.getId().then(id => {
    networkId = id;
    const chainInfo = getDataChains(id, 'chainId')[0];

    networkName = chainInfo && (chainInfo.network || chainInfo.name);
  });
  // web3.currentProvider.chainId
  // networkName = await web3.eth.net.getNetworkType();

  // chainName = getNetwork(chainId);
  // if (provider.isFortmatic) {

  //   chainName = await provider.fm.ethNetwork;
  // } else {
  //   // chainId = await web3.currentProvider.networkVersion;
  // }
  console.log(networkName);
  document.web3network = networkName;
  // Load chain information over an HTTP API
  // const chainData = await EvmChains.getChain(chainId);

  if (networkName) {
    document.querySelector('.network-name').textContent = networkName;
    document.querySelector('.wallet-network').classList.remove('rinkeby', 'mainnet');
    document.querySelector('.wallet-network').classList.add(networkName.split(' ').join('-'));
  }

  document.querySelector('#wallet-btn').innerText = 'Change Wallet';

  // Get list of accounts of the connected wallet
  const accounts = await web3.eth.getAccounts();

  // MetaMask does not give you all accounts, only the selected account
  console.log('Got accounts', accounts);
  selectedAccount = accounts[0] || provider.account;
  // selectedAccount = '0x1402e01ba957e030200ec21e1417dc32c11e486b';
  cb_address = selectedAccount;

  document.querySelector('.selected-account').textContent = truncate(selectedAccount);

  const template = document.querySelector('#template-balance');
  const accountContainer = document.querySelector('#wallet-accounts');

  // Purge UI elements any previously loaded accounts
  accountContainer.innerHTML = '';

  if (provider.isFortmatic) {
    let fortmaticBalance = await provider.fm.user.getBalances();

    balance = fortmaticBalance[0].crypto_amount;
    humanFriendlyBalance = fortmaticBalance[0].crypto_amount_display;
    console.log('humanFriendlyBalance', humanFriendlyBalance);

    const clone = template.content.cloneNode(true);

    clone.querySelector('.wallet-address').textContent = truncate(selectedAccount);
    clone.querySelector('.wallet-address').setAttribute('data-address', selectedAccount);
    clone.querySelector('.wallet-balance').textContent = `${humanFriendlyBalance} ETH`;
    accountContainer.appendChild(clone);
  }

  // Go through all accounts and get their ETH balance
  const rowResolvers = accounts.filter((val, indx, orig) => orig.indexOf(val) === indx).map(async(address) => {

    if (!accounts.length || provider.isFortmatic) {
      return;
    }
    await web3.eth.getBalance(selectedAccount, function(errors, result) {
      if (errors) {
        return;
      }
      balance = result;
      const ethBalance = web3.utils.fromWei(result, 'ether');

      // ethBalance is a BigNumber instance
      // https://github.com/indutny/bn.js/
      // console.log(ethBalance)
      humanFriendlyBalance = parseFloat(ethBalance).toFixed(4);

      // Fill in the templated row and put in the document
      const clone = template.content.cloneNode(true);

      clone.querySelector('.wallet-address').textContent = truncate(address);
      clone.querySelector('.wallet-address').setAttribute('data-address', address);
      clone.querySelector('.wallet-balance').textContent = `${humanFriendlyBalance} ETH`;
      accountContainer.appendChild(clone);
    });

  });

  // Because rendering account does its own RPC commucation
  // with Ethereum node, we do not want to display any results
  // until data for all accounts is loaded
  await Promise.all(rowResolvers);
  $('.wallet-hidden').removeClass('d-none');
  displayProvider();
  // Display fully loaded UI for wallet data
  // document.querySelector("#prepare").style.display = "none";
  // document.querySelector("#connected").style.display = "block";
  walletStateChanges();
  $('.wallet-option').on('click', changeWallet);
  document.dispatchEvent(eventDataWalletReady);
}

function changeWallet(e) {
  e.stopPropagation();
  selectedAccount = $(e.currentTarget).children('.wallet-address').data('address');
  $('.selected-account').text(truncate(selectedAccount));
}

// const provider = await web3Modal.connect();
// web3Modal.providers.push({name: 'QRcode', onClick: qrcodeConnect});
// web3Modal.connect().then(function(provider) {
//   window.web3 = new Web3(provider);
// });
function createImg(source) {
  let elem = document.querySelector('#navbarDropdownWallet');
  let icon = document.querySelector('.provider-icon');
  let imgProvider = document.querySelector('.image-provider');

  if (!imgProvider) {
    imgProvider = document.createElement('img');
    imgProvider.classList.add('image-provider');
    elem.insertBefore(imgProvider, icon);
  }

  if (!source) {
    icon.classList.remove('d-none');
    return imgProvider.parentNode.removeChild(imgProvider);
  }
  icon.classList.add('d-none');
  imgProvider.src = source.logo;
  imgProvider.width = 24;

}

function displayProvider() {
  let image = web3Modal.providerController.getProvider(web3Modal.providerController.cachedProvider);

  createImg(image);
}

async function switchChain(id) {
  const web3 = new Web3(provider);
  const providerName = window.Web3Modal.getInjectedProviderName();
  const chainInfo = getDataChains(Number(id), 'chainId')[0];
  const chainId = Web3.utils.numberToHex(chainInfo.chainId);

  try {
    await web3.currentProvider.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId }]
    });
  } catch (switchError) {
    // This error code indicates that the chain has not been added to MetaMask
    if (switchError.code === 4902) {

      try {
        await web3.currentProvider.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId,
            rpcUrls: chainInfo.rpc,
            chainName: chainInfo.name,
            nativeCurrency: chainInfo.nativeCurrency,
            blockExplorerUrls: chainInfo.explorers && chainInfo.explorers.map(e => e.url)
          }]
        });
      } catch (addError) {
        if (addError.code === 4001) {
          throw new Error(`Please connect ${providerName} to ${chainInfo.name} network.`);
        } else {
          console.error(addError);
        }
      }
    } else if (switchError.code === 4001) {
      throw new Error(`Please connect ${providerName} to ${chainInfo.name} network.`);
    } else if (switchError.code === -32002) {
      throw new Error(`Please respond to a pending ${providerName} request.`);
    } else {
      console.error(switchError);
    }
  }
}

async function onConnect() {

  // Setting this null forces to show the dialogue every time
  // regardless if we play around with a cacheProvider settings
  // in our localhost.
  // TODO: A clean API needed here
  // web3Modal.providerController.cachedProvider = null;
  web3Modal.clearCachedProvider();
  // web3Modal.clearCachedProvider();

  console.log('Opening a dialog', web3Modal);
  try {
    provider = await web3Modal.connect();
  } catch (e) {
    console.log('Could not get a wallet connection', e);
    return;
  }

  console.log(provider);
  if (provider.on) {
    // Subscribe to accounts change
    provider.on('accountsChanged', (accounts) => {
      console.log('accountsChanged');
      fetchAccountData(provider);
    });

    // Subscribe to chainId change
    provider.on('chainChanged', (chainId) => {
      console.log('chainChanged');
      fetchAccountData(provider);
    });
  }

  await refreshAccountData();
}

async function onDisconnect() {

  console.log('Killing the wallet connection', provider);

  // TODO: MetamaskInpageProvider does not provide disconnect?
  if (provider.close) {
    await provider.close();
  }
  provider = null;

  web3Modal.clearCachedProvider();
  displayProvider();

  selectedAccount = null;

  $('.wallet-hidden').addClass('d-none');
  document.querySelector('#wallet-btn').innerText = 'Connect Wallet';
  document.querySelector('.wallet-network').classList.remove('rinkeby', 'mainnet');
  cleanUpWalletData();

  document.dispatchEvent(eventWalletDisconnect);

  // Set the UI back to the initial state
  // document.querySelector("#prepare").style.display = "block";
  // document.querySelector("#connected").style.display = "none";
}

function cleanUpWalletData() {
  selectedAccount = undefined;
  balance = undefined;
  chainId = undefined;
  networkId = undefined;
  networkName = undefined;
  chainName = undefined;
  humanFriendlyBalance = undefined;
}

async function refreshAccountData() {

  // If any current data is displayed when
  // the user is switching acounts in the wallet
  // immediate hide this data
  // document.querySelector("#connected").style.display = "none";
  // document.querySelector("#prepare").style.display = "block";

  // Disable button while UI is loading.
  // fetchAccountData() will take a while as it communicates
  // with Ethereum node via JSON-RPC and loads chain data
  // over an API call.
  // document.querySelector('#wallet-btn').setAttribute('disabled', 'disabled');
  document.querySelector('#wallet-btn').innerText = 'Change Wallet';
  cleanUpWalletData();
  await fetchAccountData(provider);
  // document.querySelector('#wallet-btn').removeAttribute('disabled');
}


$('.selected-account').click(function(e) {
  let input = $(`<input type="text" value="${selectedAccount}" />`);

  input.appendTo('body');
  input.select();
  document.execCommand('copy');
  input.remove();
});

window.addEventListener('load', async() => {
  if (!document.contxt['github_handle']) {
    return;
  }

  initWallet();
  document.querySelector('#wallet-btn').addEventListener('click', onConnect);
  document.querySelector('#btn-disconnect').addEventListener('click', onDisconnect);

  if (web3Modal.cachedProvider) {
    try {
      if (web3Modal.cachedProvider === 'injected' && window.Web3Modal.getInjectedProviderName() === 'MetaMask') {
        // hack for metamask
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });

        if (!accounts.length) {
          throw new Error('Metamask is not enabled');
        }
      }
      provider = await web3Modal.connect();
    } catch (e) {
      console.log('Could not get a wallet connection', e);
      return;
    }

    if (web3Modal.providerController.cachedProvider) {
      console.log(web3Modal.providerController.cachedProvider);
      fetchAccountData(provider);
    }
    if (provider.isMetaMask) {
      console.log('metamask');
      window.ethereum.on('accountsChanged', function(accounts) {
        console.log('accountsChanged');
        fetchAccountData(provider);
      });
      window.ethereum.on('chainChanged', function(networkId) {
        console.log('chainChanged');
        fetchAccountData(provider);
      });
    }
  }
});


let minABI = [
  // balanceOf
  {
    'constant': true,
    'inputs': [{
      'name': '_owner',
      'type': 'address'
    }],
    'name': 'balanceOf',
    'outputs': [{
      'name': 'balance',
      'type': 'uint256'
    }],
    'type': 'function'
  },
  // decimals
  {
    'constant': true,
    'inputs': [],
    'name': 'decimals',
    'outputs': [{
      'name': '',
      'type': 'uint8'
    }],
    'type': 'function'
  },
  // symbol
  {
    'constant': true,
    'inputs': [],
    'name': 'symbol',
    'outputs': [{
      'name': '',
      'type': 'string'
    }],
    'payable': false,
    'type': 'function'
  },
  // token name
  {
    'constant': true,
    'inputs': [],
    'name': 'name',
    'outputs': [{
      'name': '',
      'type': 'string'
    }],
    'payable': false,
    'type': 'function'
  },
  // allowance
  {
    'constant': true,
    'inputs': [{
      'name': '_owner',
      'type': 'address'
    },
    {
      'name': '_spender',
      'type': 'address'
    }],
    'name': 'allowance',
    'outputs': [{
      'name': 'remaining',
      'type': 'uint256'
    }],
    'payable': false,
    'type': 'function'
  },
  // approve allowance
  {
    'constant': false,
    'inputs': [{
      'name': '_spender',
      'type': 'address'
    },
    {
      'name': '_value',
      'type': 'uint256'
    }],
    'name': 'approve',
    'outputs': [{
      'name': 'success',
      'type': 'bool'
    }],
    'payable': false,
    'type': 'function'
  }
];

/**
 *  * Check the balance of a ERC20 token.
 *  * @param {string} tokenAddress - the ERC20 token address
 *  */
async function getTokenBalances(tokenAddress) {
  let balance;
  let decimals;
  let symbol;
  let name;
  let result;
  let balanceHuman;
  // The minimum ABI to get ERC20 Token balance

  // Get ERC20 Token contract instance
  let tokensContract = new web3.eth.Contract(minABI, tokenAddress);

  // Call balanceOf function
  balance = tokensContract.methods.balanceOf(selectedAccount).call({from: selectedAccount});
  decimals = tokensContract.methods.decimals().call({from: selectedAccount});
  symbol = tokensContract.methods.symbol().call({from: selectedAccount});
  name = tokensContract.methods.name().call({from: selectedAccount});
  balanceHuman = Number(await balance) / Math.pow(10, await decimals);

  try {
    result = {
      'balance': balanceHuman,
      'balance_rounded': Math.round(balanceHuman * 10) / 10,
      'symbol': await symbol,
      'name': await name
    };
    return result;
  } catch (error) {
    console.log(error);
  }
}

/**
 *  * Check the allowance remaining on a contract address.
 *  * @param {string} address - the contract address
 *  * @param {string} tokenAddress - the token address contract
 *  */
async function getAllowance(address, tokenAddress) {
  let allowance;
  let tokensContract = new web3.eth.Contract(minABI, tokenAddress);

  allowance = tokensContract.methods.allowance(selectedAccount, address).call({from: selectedAccount});
  return await allowance;
}

/**
 *  * Approve allowance for a contract address.
 *  * @param {string} address - the contract address
 *  * @param {string} tokenAddress - the token address contract
 *  * @param {string} weiamount (optional)- the token address
 *  */
async function approveAllowance(address, tokenAddress, weiamount) {
  let defaultAmount = new web3.utils.BN(BigInt(10 * 18 * 9999999999999999999999999999999999999999999999999999)).toString();
  let amount = weiamount || defaultAmount; // uint256
  let approved;
  let tokensContract = new web3.eth.Contract(minABI, tokenAddress);

  approved = tokensContract.methods.approve(address, amount).send({from: selectedAccount});
  return await approved;
}
