/* eslint-disable no-console */

/** Used to populate & send token claim transaction
 *  For now it's just sending a simple tx
 *  Next step is to load up a tx call to make claim
 */

$(document).ready(function() {
  $('#send').on('click', async function(e) {
      
    e.preventDefault();
    if ($(this).hasClass('disabled'))
      return;
    loading_button($(this));
    
    if (!provider) {
      await onConnect();
    }
     
    // debugging
    console.log('successfully loaded send-claim.js!');

    var user_id = document.getElementById('user_id').textContent;
    var user_address = document.getElementById('user_address').textContent;
    var user_amount = document.getElementById('user_amount').textContent;
    var msg_hash_hex = document.getElementById('msg_hash_hex').textContent;
    var eth_signed_message_hash_hex = document.getElementById('eth_signed_message_hash_hex').textContent;
    var eth_signed_signature_hex = document.getElementById('eth_signed_signature_hex').textContent;
    var accept_tos = $('#tos').is(':checked');
    var tokenName = 'ETH'; // just used for getting landing page to load for now

    console.log(user_id, user_address, user_amount, msg_hash_hex, eth_signed_message_hash_hex, eth_signed_signature_hex);


    var success_callback = function(txid) {
    
      startConfetti();
      var url = 'https://' + etherscanDomain() + '/tx/' + txid;
          
      $('#loading_trans').html('This transaction has been sent 👌');
      $('#send_eth').css('display', 'none');
      $('#send_eth_done').css('display', 'block');
      $('#tokenName').html(tokenName);
      $('#trans_link').attr('href', url);
      $('#trans_link2').attr('href', url);
      unloading_button($(this));
        
      /* some tracking code? idk.
          dataLayer.push({
            'event': 'sendtip',
            'category': 'sendtip',
            'action': 'sendtip'
          });
          */
    };
        
    var failure_callback = function() {
      unloading_button($('#send'));
    };

    // lets just register the click for now
    console.log('end on ready!');
    return sendClaim(user_id, user_address, user_amount, msg_hash_hex, eth_signed_message_hash_hex, eth_signed_signature_hex, accept_tos, success_callback, failure_callback);
    
  });

});

function sendClaim(user_id, user_address, user_amount, msg_hash_hex, eth_signed_message_hash_hex, eth_signed_signature_hex, accept_tos, success_callback, failure_callback) {
  // check web3 enabled
  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You must have a web3 enabled browser to do this.  Please download Metamask.') }, 'warning');
    failure_callback();
    return;
  }

  // setup - who will se send the TX from?
  if (selectedAccount === 'undefined') {

    _alert({ message: gettext('You must unlock & enable Gitcoin via your web3 wallet to continue.') }, 'warning');
    failure_callback();
    return;
  }
  const fromAccount = selectedAccount;

  // make sure it's check summ'd address and strip quotes
  const destinationAccount = web3.utils.toChecksumAddress(user_address.replace(/\"/g, ''));

  // for now, until we get more info on how amount will be obtained and supplied
  const amountInDenom = user_amount;
    
  // maybe we want to manually check ETH balance here?

  // validation -
    
  if (!isNumeric(amountInDenom) || amountInDenom == 0) {
    _alert({ message: gettext('You must enter an number for the amount!') }, 'warning');
    failure_callback();
    return;
  }
    
  if (!(web3.utils.isAddress(destinationAccount))) {
    _alert({ message: gettext('Ethereum destination address is not valid!') }, 'warning');
    failure_callback();
    return;
  }

  if (!accept_tos) {
    _alert({ message: gettext('You must accept the terms.') }, 'warning');
    failure_callback();
    return;
  }
  var post_send_callback = function(errors, txid) {
    indicateMetamaskPopup(true);
    if (errors) {
      _alert({ message: gettext('There was an error.') }, 'warning');
      failure_callback();
    } else {
      success_callback(txid);
    }
     
  };

  indicateMetamaskPopup();

  web3.eth.sendTransaction({
    from: fromAccount,
    to: destinationAccount,
    value: amountInDenom
  }).once('transactionHash', (txnHash, errors) => {
    if (errors) {
      console.log(errors);
    }
    console.log(txnHash);
    post_send_callback(errors, txnHash);
  });

} // end sendClaim

// helper functions

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

var etherscanDomain = function() {
  var etherscanDomain = 'etherscan.io';
  
  if (document.web3network == 'custom network') {
    // testrpc
    etherscanDomain = 'localhost';
  } else if (document.web3network == 'rinkeby') {
    // rinkeby
    etherscanDomain = 'rinkeby.etherscan.io';
  } else {
    // mainnet
  }
  return etherscanDomain;
};