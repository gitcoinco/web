var signed_message_payload
// let BN;

/// request.user.id, request.POST.get('address') 
// post into microservice 
/// payback (sign msg)

$( document ).ready(function() {
    console.log( "ready!" );
    
$(document).on('click', '#beginClaim', (event) => {
    console.log('-->#beginClaim successfully triggered')
    console.log('selectedAccount', selectedAccount);
    // var sendForm = fetchData('/quadraticlands/claim2', 'POST', {'address':selectedAccount}, {'X-CSRFToken': csrftoken})
    

    var sendForm = fetchData('/quadraticlands/claim2', 'POST', {'address':selectedAccount}, {'X-CSRFToken': csrftoken})

    $.when(sendForm).then((response, status, statusCode) => {
        // for debugging, remove for prod 
        // console.log('POST RETURNED!', statusCode, response, status)
        
        // if we don't get a 200 from the Ethereum Message Signing Service then return error  
        if (statusCode.status != 200) {
            /**  
            * I need to confirm/deny _alert will trigger here, I don't think it's all setup correctly yet 
            * _alert is currently set/driven by web3alert.js included directly in demo2.html 
            * as needed, we can adjust and change that so that all our _alerts are imported on base.html 
            **/
            return _alert(response.msg, 'error');
        }
       
        // setup & send our contract call 
        setupGTCTokenClaim(response)


    });

});

async function testClaim(response) {
    try {
        console.log('testclaim: trigger successfully!');
        console.log('testClaim-response: ', response)
        console.log('user_id', response.user_id)
        const network = checkWeb3();
        
        // get current active wallet account 
        [user_active_account] = await web3.eth.getAccounts();
        console.log('user_active_account', user_active_account);

        //if response['user_address']

    } catch(error) { 
        console.log(error);
        handleError(error);
    }

}

async function setupGTCTokenClaim(emss_response) {
    
    // if user messes with these, the contract will reject the claim
    // for this reason, extensive validation is not necessary     
    const user_id = emss_response.user_id;
    const user_amount = emss_response.user_amount;
    const user_address_cleaned = web3.utils.toChecksumAddress(emss_response["user_address"].replace(/\"/g, '')); // make sure it's check summ'd address and strip quotes
    const eth_signed_message_hash_hex = emss_response.eth_signed_message_hash_hex;
    const eth_signed_signature_hex = emss_response.eth_signed_signature_hex;
    
    try {
      // confirm we have a working web3 connection, if not, bail   
      const network = checkWeb3();
       
      // get the current active account/address from the user 
      // not needed here unless we want to do a final check to confirm something with active address
      // i dont think so tho...? 
      [user] = await web3.eth.getAccounts();
  
      // TODO - move token contract addy to env or standard abi.js file
      // ZW: added new Rinkeby tokendist contract 10/29/2020
      // also, we will want to update the contract ABI at somepoint. it's old but still works as the function name is the same :) 
      const tokenDistributor = await new web3.eth.Contract(
        token_distributor_abi,
        '0xa4c8B8a59805F6B049b977296881CE76f538D7C4'
      );
          
      const claimGTCtokens = () => {
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
      claimGTCtokens();
  
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


}); // document.on ready --> 




/**
contractmethod(signmsg).on('transactionhash', function(txid) {
    var sendtxid = fetchData('/sveclaimed',
    'POST',
    {'txid':txid}
    )
    $.when(sendtxid).then(function(payback){ return payback })
}
*/