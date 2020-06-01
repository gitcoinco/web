const Web3Modal = window.Web3Modal.default;
const WalletConnectProvider = window.WalletConnectProvider.default;

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

const qrcodeConnect = function() {
  // return new Promise(async (resolve, reject) => {
  //   const qrcode = true
  //   const provider = qrcode.getProvider();
  //   provider.qrcode = qrcode;
  //   try {
  //     await provider.enable();
  //     resolve(provider);
  //   } catch (error) {
  //     return reject(error);
  //   }
  // });
  // return true;
  // localStorage['WEB3_CONNECT_CACHED_PROVIDER'] = '"injected"';
  // web3Modal.toggleModal();


  const provider = {
      chainId: 1,
      account: 'none'
    };
    // if (window.ethereum) {
    //   provider = window.ethereum;
    //   try {
    //     await window.ethereum.enable();
    //   } catch (error) {
    //     throw new Error("User Rejected");
    //   }
    // } else if (window.web3) {
    //   provider = window.web3.currentProvider;
    // } else {
    //   throw new Error("No Web3 Provider found");
    // }
    return provider;


};

function initWallet() {
  // window.Web3Modal.providers.push({
  //   id: 'injected',
  //   name: 'QRcode',
  //   logo: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='512' height='512' fill='none'%3E%3Cpath fill='url(%23paint0_radial)' fill-rule='evenodd' d='M256 0c141.385 0 256 114.615 256 256S397.385 512 256 512 0 397.385 0 256 114.615 0 256 0z' clip-rule='evenodd'/%3E%3Cpath fill='%23fff' d='M165 243v-78h78v78h-78zm16.25-61.75v45.5h45.5v-45.5h-45.5zM269 165h78v78h-78v-78zm61.75 61.75v-45.5h-45.5v45.5h45.5zM165 347v-78h78v78h-78zm16.25-61.75v45.5h45.5v-45.5h-45.5zm13 13h19.5v19.5h-19.5v-19.5zm0-104h19.5v19.5h-19.5v-19.5zm123.5 19.5h-19.5v-19.5h19.5v19.5zM334 269h13v52h-52v-13h-13v39h-13v-78h39v13h26v-13zm0 65h13v13h-13v-13zm-26 0h13v13h-13v-13z'/%3E%3Cdefs%3E%3CradialGradient id='paint0_radial' cx='0' cy='0' r='1' gradientTransform='translate(9.283 256) scale(502.717)' gradientUnits='userSpaceOnUse'%3E%3Cstop stop-color='%237C89FF'/%3E%3Cstop offset='1' stop-color='%231E34FF'/%3E%3C/radialGradient%3E%3C/defs%3E%3C/svg%3E",
  //   type: 'injected',
  //   check: 'isQRcode',
  //   styled: {
  //     noShadow: true
  //   }
  // });

  // custom code for qcode
  // "custom-qrcode": {
  //   display: {
  //     logo: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='512' height='512' fill='none'%3E%3Cpath fill='url(%23paint0_radial)' fill-rule='evenodd' d='M256 0c141.385 0 256 114.615 256 256S397.385 512 256 512 0 397.385 0 256 114.615 0 256 0z' clip-rule='evenodd'/%3E%3Cpath fill='%23fff' d='M165 243v-78h78v78h-78zm16.25-61.75v45.5h45.5v-45.5h-45.5zM269 165h78v78h-78v-78zm61.75 61.75v-45.5h-45.5v45.5h45.5zM165 347v-78h78v78h-78zm16.25-61.75v45.5h45.5v-45.5h-45.5zm13 13h19.5v19.5h-19.5v-19.5zm0-104h19.5v19.5h-19.5v-19.5zm123.5 19.5h-19.5v-19.5h19.5v19.5zM334 269h13v52h-52v-13h-13v39h-13v-78h39v13h26v-13zm0 65h13v13h-13v-13zm-26 0h13v13h-13v-13z'/%3E%3Cdefs%3E%3CradialGradient id='paint0_radial' cx='0' cy='0' r='1' gradientTransform='translate(9.283 256) scale(502.717)' gradientUnits='userSpaceOnUse'%3E%3Cstop stop-color='%237C89FF'/%3E%3Cstop offset='1' stop-color='%231E34FF'/%3E%3C/radialGradient%3E%3C/defs%3E%3C/svg%3E",
  //     name: "QRcode",
  //     type: "qrcode",
  //     check: "isQRcode",
  //     description: "Connect to your example provider account"
  //   },
  //   package: qrcodeConnect,
  //   connector: async (ProviderPackage) => {
  //     console.log(ProviderPackage)
  //       const provider = new ProviderPackage();

  //       // await provider.enable()

  //       // return true;
  //       // let provider = null;
  //       // if (window.ethereum) {
  //       //   provider = window.ethereum;
  //       //   try {
  //       //     await window.ethereum.enable();
  //       //   } catch (error) {
  //       //     throw new Error("User Rejected");
  //       //   }
  //       // } else if (window.web3) {
  //       //   provider = window.web3.currentProvider;
  //       // } else {
  //       //   throw new Error("No Web3 Provider found");
  //       // }
  //       return provider;
  //   }
  // }


  // Determine if we're on prod or not
  const isProd = document.location.href.startsWith('https://gitcoin.co');
  const formaticKey = isProd ? document.contxt['fortmatic_live_key'] : document.contxt['fortmatic_test_key'];
  const providerOptions = {
    authereum: {
      'package': Authereum
    },
    fortmatic: {
      'package': Fortmatic,
      options: {
        key: formaticKey
      }
    },
    walletconnect: {
      package: WalletConnectProvider,
      options: {
        infuraId: "1e0a90928efe4bb78bb1eeceb8aacc27",
      }
    },


  };
  const network = isProd ? 'mainnet' : 'rinkeby';

  web3Modal = new Web3Modal({
    network,
    cacheProvider: true,
    providerOptions
  });


}

async function fetchAccountData(provider) {

  // Get a Web3 instance for the wallet
   web3 = new Web3(provider);

  console.log("Web3 instance is", web3);

  // Get connected chain id from Ethereum node
  chainId = await web3.eth.currentProvider.chainId;
  networkId = await web3.eth.net.getId();
  // web3.currentProvider.chainId
  networkName = await web3.eth.net.getNetworkType()
  // chainName = getNetwork(chainId);
  // if (provider.isFortmatic) {

  //   chainName = await provider.fm.ethNetwork;
  // } else {
  //   // chainId = await web3.currentProvider.networkVersion;
  // }
  console.log(networkName)
  document.web3network = networkName;
  // Load chain information over an HTTP API
  // const chainData = await EvmChains.getChain(chainId);

  document.querySelector(".network-name").textContent = networkName;
  document.querySelector(".wallet-network").classList.remove('rinkeby', 'mainnet')
  document.querySelector(".wallet-network").classList.add(networkName.split(' ').join('-'))

  // Get list of accounts of the connected wallet
  const accounts = await web3.eth.getAccounts();
  // const accounts = await web3.eth.accounts;

  // if (!accounts.length) {
  //   console.log(accounts, 'dentro')
  //   accounts = [provider.account];
  // }
  // console.log(accounts, 'fora')


  // MetaMask does not give you all accounts, only the selected account
  console.log("Got accounts", accounts);
  selectedAccount = accounts[0] || provider.account;
  cb_address = selectedAccount;

  document.querySelector(".selected-account").textContent = truncate(selectedAccount);

  // Get a handl
  const template = document.querySelector("#template-balance");
  const accountContainer = document.querySelector("#accounts");

  // Purge UI elements any previously loaded accounts
  accountContainer.innerHTML = '';

  console.log('provider', provider)
  if (provider.isFortmatic) {
    console.log('is fortmatic')
    let fortmaticBalance = await provider.fm.user.getBalances()
    console.log(fortmaticBalance)
    balance = fortmaticBalance[0].crypto_amount;
    humanFriendlyBalance = fortmaticBalance[0].crypto_amount_display;
    console.log('humanFriendlyBalance', humanFriendlyBalance)

    const clone = template.content.cloneNode(true);
    clone.querySelector(".address").textContent = truncate(selectedAccount);
    clone.querySelector(".balance").textContent = humanFriendlyBalance;
    accountContainer.appendChild(clone);
  }

  // Go through all accounts and get their ETH balance
  const rowResolvers = accounts.map(async (address) => {
    // const balance = await web3.eth.getBalance(address);
    // async function(){
      // await web3.eth.getBalance(address, function(sus,erro) {
      //   console.log(sus, erro)
      //   balance = sus;
      // })

      // var bal = await provider.fm.user.getBalances()
    if (!accounts.length || provider.isFortmatic) {
      return;
    }
    await web3.eth.getBalance(selectedAccount, function(errors, result) {
      if (errors) {
        return;
      }
      balance = result
      const ethBalance = web3.utils.fromWei(result, "ether");
      console.log(result)
      // console.log(web3.fromWei(result, "ether"));
      // }
      // const ethBalance = await balance.toNumber();
      // const ethBalance = web3.fromWei(balance, "ether");
      // ethBalance is a BigNumber instance
      // https://github.com/indutny/bn.js/
      // console.log(ethBalance)
      humanFriendlyBalance = parseFloat(ethBalance).toFixed(4);

      // Fill in the templated row and put in the document
      const clone = template.content.cloneNode(true);
      clone.querySelector(".address").textContent = truncate(address);
      clone.querySelector(".balance").textContent = humanFriendlyBalance;
      accountContainer.appendChild(clone);
    })

  });

  // Because rendering account does its own RPC commucation
  // with Ethereum node, we do not want to display any results
  // until data for all accounts is loaded
  await Promise.all(rowResolvers);
  $('.wallet-hidden').removeClass('d-none');
  displayProvider()
  // Display fully loaded UI for wallet data
  // document.querySelector("#prepare").style.display = "none";
  // document.querySelector("#connected").style.display = "block";
}



// const provider = await web3Modal.connect();


// web3Modal.providers.push({name: 'QRcode', onClick: qrcodeConnect});
// web3Modal.connect().then(function(provider) {
//   window.web3 = new Web3(provider);
// });
function createImg(source) {
  let elem = document.querySelector("#navbarDropdownWallet");
  let icon = document.querySelector(".provider-icon");
  let imgProvider = document.querySelector(".image-provider");

  if (!imgProvider) {
    imgProvider = document.createElement('img');
    imgProvider.classList.add('image-provider')
    elem.appendChild(imgProvider);
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

  let image = web3Modal.providerController.getProvider(web3Modal.providerController.cachedProvider)
  createImg(image)

}

async function onConnect() {

  // Setting this null forces to show the dialogue every time
  // regardless if we play around with a cacheProvider settings
  // in our localhost.
  // TODO: A clean API needed here
  web3Modal.providerController.cachedProvider = null;
    // web3Modal.clearCachedProvider();

  console.log("Opening a dialog", web3Modal);
  try {
    provider = await web3Modal.connect();
  } catch(e) {
    console.log("Could not get a wallet connection", e);
    return;
  }

  console.log(provider)
  if (provider.on){
    // Subscribe to accounts change
    provider.on("accountsChanged", (accounts) => {
      fetchAccountData();
    });

    // Subscribe to chainId change
    provider.on("chainChanged", (chainId) => {
      fetchAccountData();
    });

    // Subscribe to networkId change
    provider.on("networkChanged", (networkId) => {
      fetchAccountData();
    });
  }

  // web3Modal.providerController.injectedProvider.logo



  await refreshAccountData();
}

async function onDisconnect() {

  console.log("Killing the wallet connection", provider);

  // TODO: MetamaskInpageProvider does not provide disconnect?
  if(provider.close) {
    await provider.close();

  }
  provider = null;

  web3Modal.clearCachedProvider()
  displayProvider()

  selectedAccount = null;

  $('.wallet-hidden').addClass('d-none');

  // Set the UI back to the initial state
  // document.querySelector("#prepare").style.display = "block";
  // document.querySelector("#connected").style.display = "none";
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
  document.querySelector("#wallet-btn").setAttribute("disabled", "disabled")
  await fetchAccountData(provider);
  document.querySelector("#wallet-btn").removeAttribute("disabled")
}


$('.selected-account').click(function(e) {
  let input = $(`<input type="text" value="${selectedAccount}" />`);
  input.appendTo('body');
  input.select();
  document.execCommand('copy');
  input.remove();
});

window.addEventListener('load', async () => {
  initWallet();
  if (web3Modal.cachedProvider) {
    try {
      provider = await web3Modal.connect();
    } catch(e) {
      console.log("Could not get a wallet connection", e);
      return;
    }

    if (web3Modal.providerController.cachedProvider) {
      console.log(web3Modal.providerController.cachedProvider)
      fetchAccountData(provider);
    }
    if (provider.isMetaMask) {
      console.log('metamask')
      window.ethereum.on('accountsChanged', function (accounts) {
      console.log('accountsChanged')

        fetchAccountData();
      })
      window.ethereum.on('networkChanged', function (networkId) {
      console.log('networkChanged')

        fetchAccountData();
      })
    }
  }
  document.querySelector("#wallet-btn").addEventListener("click", onConnect);
  document.querySelector("#btn-disconnect").addEventListener("click", onDisconnect);
});
