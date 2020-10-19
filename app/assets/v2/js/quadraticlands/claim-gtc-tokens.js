// GTC token constants

// it wouldn't pull abi from abi.js so I put it here
// let token_distributor_abi = [ { "inputs":[ { "internalType":"address", "name":"_token", "type":"address" }, { "internalType":"address", "name":"_signer", "type":"address" } ], "stateMutability":"nonpayable", "type":"constructor" }, { "anonymous":false, "inputs":[ { "indexed":false, "internalType":"uint256", "name":"index", "type":"uint256" }, { "indexed":false, "internalType":"address", "name":"account", "type":"address" }, { "indexed":false, "internalType":"uint256", "name":"amount", "type":"uint256" } ], "name":"Claimed", "type":"event" }, { "inputs":[ { "internalType":"uint32", "name":"user_id", "type":"uint32" }, { "internalType":"address", "name":"user_address", "type":"address" }, { "internalType":"uint256", "name":"user_amount", "type":"uint256" }, { "internalType":"bytes32", "name":"eth_signed_message_hash_hex", "type":"bytes32" }, { "internalType":"bytes", "name":"eth_signed_signature_hex", "type":"bytes" } ], "name":"claimTokens", "outputs":[], "stateMutability":"nonpayable", "type":"function" }, { "inputs":[ { "internalType":"uint32", "name":"user_id", "type":"uint32" }, { "internalType":"address", "name":"user_address", "type":"address" }, { "internalType":"uint256", "name":"user_amount", "type":"uint256" }, { "internalType":"bytes32", "name":"eth_signed_message_hash_hex", "type":"bytes32" } ], "name":"confirmMessage", "outputs":[ { "internalType":"bool", "name":"", "type":"bool" } ], "stateMutability":"pure", "type":"function" }]
let BN;

$(document).on('click', '#WTF', (event) => {
  console.log('WTF HEREHERHERE!');
});

$(document).on('click', '#claim', (event) => {
  event.preventDefault();
  const user_id = document.getElementById('user_id').textContent;
  const user_address = document.getElementById('user_address').textContent;
  const user_amount = document.getElementById('user_amount').textContent;
  const eth_signed_message_hash_hex = document.getElementById('eth_signed_message_hash_hex').textContent;
  const eth_signed_signature_hex = document.getElementById('eth_signed_signature_hex').textContent;
  const accept_tos = $('#tos').is(':checked');
    
  // Validations
  
  // make sure it's check summ'd address and strip quotes
  const user_address_cleaned = web3.utils.toChecksumAddress(user_address.replace(/\"/g, ''));

  // for now, until we get more info on how amount will be obtained and supplied
  const amountInDenom = user_amount;

  if (!isNumeric(amountInDenom) || amountInDenom == 0) {
    _alert({ message: gettext('You must enter an number for the amount!') }, 'warning');
    // failure_callback();
    return;
  }
  /**
    if (!(web3.utils.isAddress(destinationAccount))) {
        _alert({ message: gettext('Ethereum destination address is not valid!') }, 'warning');
        // failure_callback();
        return;
    }
    */
  if (!accept_tos) {
    _alert({ message: gettext('You must accept the terms.') }, 'warning');
    // failure_callback();
    return;
  }

  claimGTCTokens(user_id, user_address_cleaned, user_amount, eth_signed_message_hash_hex, eth_signed_signature_hex);
});


async function claimGTCTokens(user_id, user_address_cleaned, user_amount, eth_signed_message_hash_hex, eth_signed_signature_hex) {
    
  try {
    const network = checkWeb3();

    BN = web3.utils.BN;
    [user] = await web3.eth.getAccounts();

    // move token contract addy to env or standard abi.js file
    const tokenDistributor = await new web3.eth.Contract(
      token_distributor_abi,
      '0x2d421946b6Ba59e336B6d8D8C426537c3FfBb5f4'
    );
        
    const claimGTCtoken = () => {
      // waitingState(true);
      tokenDistributor.methods
        .claimTokens(user_id, user_address_cleaned, user_amount, eth_signed_message_hash_hex.replace(/\"/g, ''), eth_signed_signature_hex.replace(/\"/g, ''))
      // We hardcode gas limit otherwise web3's `estimateGas` is used and this will show the user
      // that their transaction will fail because the approval tx has not yet been confirmed
        .send({ from: user, gasLimit: '300000' })
        .on('transactionHash', async function(transactionHash) {
    
          _alert('Your claim has been broadcast to the network!.', 'success', 5000);
     
          const successMsg = 'Congratulations, your token purchase was successful!';
          const errorMsg = 'Oops, something went wrong purchasing the token. Please try again or contact support@gitcoin.co';

        }).on('error', (error, receipt) => {
          // waitingState(false);
          handleError(error);
        });
        
    };
     
    // now we run the function.
    indicateMetamaskPopup();
    claimGTCtoken();

  } catch (error) {
    handleError(error);
  }
}

function checkNetwork() {
  const supportedNetworks = [ 'rinkeby', 'mainnet' ];
  
  if (!supportedNetworks.includes(document.web3network)) {
    _alert('Unsupported network', 'error');
    throw new Error('Please connect a wallet');
  }
  return document.web3network;
}

function checkWeb3() {
  if (!web3) {
    _alert('Please connect a wallet', 'error');
    throw new Error('Please connect a wallet');
  }
  return checkNetwork();
}

function handleError(err) {
  console.error(err);
  let message = 'There was an error';
  
  if (err.message)
    message = err.message;
  else if (err.msg)
    message = err.msg;
  else if (err.responseJSON)
    message = err.responseJSON.message;
  else if (typeof err === 'string')
    message = err;
  
  _alert(message, 'error');
  indicateMetamaskPopup(true);
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}