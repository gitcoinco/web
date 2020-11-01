var signed_message_payload
let BN;

/// request.user.id, request.POST.get('address') 
// post into microservice 
/// payback (sign msg)

window.addEventListener('dataWalletReady', function(e) {
    // $('.wallet-address').html(selectedAccount) //class
    $('#wallet-address').html(selectedAccount)
 }, false);

// $( document ).ready(function() {
//     console.log( "ready!" );
   
$(document).on('click', '#beginClaim', (event) => {
    console.log('-->#beginClaim successfully triggered')

    // confirm we have a working web3 connection, if not, return error 
    try {
        const network = checkWeb3();
    } catch (error) {
        // @Richard, this is where we could trigger a user notification 
        // that they are not connected to a wallet/web3 and thus the claim will not proceed. 
        return console.log('Please confirm you have a wallet connected!!')
    }

    // ZW TODO - check that eth address is_valid before proceeding? - if not valid, return 

    var getClaimData = fetchData('/quadraticlands/claim2', 'POST', {'address':selectedAccount}, {'X-CSRFToken': csrftoken})

    $.when(getClaimData).then((response, status, statusCode) => {
        // for debugging, remove for prod 
        console.log('POST RETURNED!', statusCode, response, status)
        
        // if we don't get a 200 from the Ethereum Message Signing Service then return error  
        if (statusCode.status != 200) {
            console.log('getClaimData response: ', statusCode.status )
            return //_alert(response.msg, 'error');
        }
       
        // setup & send our contract call 
        setupGTCTokenClaim(response)
        
        // used to test succesful response from the contract, this will return true provided a legit signed message and hash 
        // probably dont want to use this and setupGTCTokenClaim at once 
        // setupIsSigned(response)
        // used for debugging if you want to confirm calling function after POST
        // will be removed for prod 
        // testClaim(response);


    });

});
async function setupIsSigned(emss_response) {
    
  const eth_signed_message_hash_hex = emss_response.eth_signed_message_hash_hex.replace(/\"/g, ''); // strip quotes 
  const eth_signed_signature_hex = emss_response.eth_signed_signature_hex.replace(/\"/g, ''); // strip quotes 
  
  try {
    // who will send the transaction? (active user wallet account)
    [user] = await web3.eth.getAccounts();
    // notes, this function calls the actual tokendist v2 ABI 
    const tokenDistributor_v2 = await new web3.eth.Contract(
      token_distributor_v2_abi,
      '0xa4c8B8a59805F6B049b977296881CE76f538D7C4'
    );
        
    const isSigned = () => {

        tokenDistributor_v2.methods
        .isSigned(eth_signed_message_hash_hex, eth_signed_signature_hex)
        .send({ from: user, gasLimit: '300000' })
        .on('transactionHash', async function(transactionHash) {})
        .on('receipt', receipt => {
              console.log('receipt:', receipt);
        })
        .on('confirmation', (confirmationNumber, receipt) => {
              if (confirmationNumber <= 5 ) {
                console.log('confirmations:', confirmationNumber, receipt);
              }
        })
        .on('error', (error) => { 
          const errorMsg = 'Oops, something went wrong with token claim. Please check transaction for more info, try again, and/or contact support@gitcoin.co';
          console.log('errorMsg',errorMsg);
        });

       
    };
    // make our contract call 
    isSigned();  
         

  } catch (error) {
    console.log('error on isClaimed: ', error)
    // handleError(error);
  }

}
async function setupGTCTokenClaim(emss_response) {
    
    // BN = web3.utils.BN;
    const user_id = emss_response.user_id;
    // const user_amount = new BN(emss_response.user_amount);
    const user_amount = emss_response.user_amount;
    const user_address_cleaned = web3.utils.toChecksumAddress(emss_response["user_address"].replace(/\"/g, '')); // make sure it's check summ'd address and strip quotes
    const eth_signed_message_hash_hex = emss_response.eth_signed_message_hash_hex.replace(/\"/g, ''); // strip quotes 
    const eth_signed_signature_hex = emss_response.eth_signed_signature_hex.replace(/\"/g, ''); // strip quotes 
    
    try {
      // who will send the transaction? (active user wallet account)
      [user] = await web3.eth.getAccounts();
      // ZW TODO - move token contract addy to env or standard abi.js file, added new Rinkeby tokendist contract 10/29/2020
      // also, we will want to update the contract ABI at some point. it's old but still works as the function name is the same :) 
      const tokenDistributor = await new web3.eth.Contract(
        token_distributor_abi,
        '0xa4c8B8a59805F6B049b977296881CE76f538D7C4'
      );
          
      const claimGTCtokens = () => {
        // waitingState(true);
               tokenDistributor.methods
          .claimTokens(user_id, user_address_cleaned, web3.utils.toWei(user_amount, 'ether'), eth_signed_message_hash_hex, eth_signed_signature_hex)
          
          /** TODO - Evaluate optimal gas settings for token claims 
          * strat: hard coded price is fallback, dynamic real time gas adjustment is optimal  - how much gas can we save? 
          *  // Legacy Note- We hardcode gas limit otherwise web3's `estimateGas` is used and this will show the user
          *  // that their transaction will fail because the approval tx has not yet been confirmed
          */
          .send({ from: user, gasLimit: '300000' })
          .on('transactionHash', async function(transactionHash) {
            // @Richard, this is where we can trigger to the PENDING screen - or whatever you want to do upon receiving the txid confirming the tx has been broadcast     
            // _alert('Your claim has been broadcast to the network!.', 'success', 5000);
            const successMsg = 'Congratulations, your token claim transaction was broadcast to the Ethereum network! ';
            console.log('successMsg', successMsg, 'txid: ', transactionHash);

            // this is not live yet, need to create DB models first before we can write txid to postgres db 
            // pushTXID2DB(transactionHash); 
            
          })
          // this was added for debug/testing - I'm not sure there is any value in having this and it will likely be removed. 
          .on('receipt', receipt => {
                console.log('receipt:', receipt);
          })
          // also added for debug/testing - I will keep it in for now in case we want to trigger an event on tx confirmation 
          .on('confirmation', (confirmationNumber, receipt) => {
                if (confirmationNumber = 1 ) {
                  console.log('confirmations:', confirmationNumber, receipt);
                }
                // @Richard, do we want to react to confirmation? 
          })
          .on('error', (error) => { 
            const errorMsg = 'Oops, something went wrong with token claim. Please check transaction for more info, try again, and/or contact support@gitcoin.co';
            console.log('errorMsg',errorMsg);
            // console.error(error)
            // waitingState(false);
            // handleError(error);
          });
        // indicateMetamaskPopup();
        // make our claim
         
      };
      //indicateMetamaskPopup();
      claimGTCtokens();  
           
 
    } catch (error) {
      console.log('error on setupTokenClaim: ', error)
      // handleError(error);
    }

  }

function pushTXID2DB(transactionHash) {
    
    // check csrf token settings for second api fetch 
    var sendForm = fetchData('/quadraticlands/write-claim-TXID', 'POST', {'txid':transactionHash}, {'X-CSRFToken': csrftoken})
    $.when(sendForm).then((response, status, statusCode) => {
        // for debugging, remove for prod 
        console.log('POST RETURNED!', statusCode, response, status)
        
        // if we don't get a 200 from the database api then we return the error 
        if (statusCode.status != 200) {
            console.log('statusCode on pushTXID2DB: ', statusCode)
            return //_alert(response.msg, 'error');
        }
   });  

}


function checkNetwork() {
    const supportedNetworks = [ 'rinkeby', 'mainnet' ];
    
    if (!supportedNetworks.includes(document.web3network)) {
      //_alert('Unsupported network', 'error');
      throw new Error;
    }
    return document.web3network;
}
  
function checkWeb3() {
    if (!web3) {
      // _alert('Please connect a wallet', 'error');
      throw new Error;
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
    
    //_alert(message, 'error');
    indicateMetamaskPopup(true);
}
  
function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

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




/**
contractmethod(signmsg).on('transactionhash', function(txid) {
    var sendtxid = fetchData('/sveclaimed',
    'POST',
    {'txid':txid}
    )
    $.when(sendtxid).then(function(payback){ return payback })
}
*/
