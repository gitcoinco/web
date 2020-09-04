// Personal token constants
// Note that this address is also duplicated in board.js
const factoryAddress = document.contxt.ptoken_factory_address;
const purchaseTokenName = 'DAI';

let BN;

$(document).on('click', '#submit_buy_token', (event) => {
  event.preventDefault();

  // Hide existing validation errors
  $('#ptokenAmount').removeClass('is-invalid');
  $('#ptokenAmount ~ .invalid-feedback').hide();
  $('#ptokenTerms').removeClass('is-invalid');
  $('#ptokenTerms ~ .invalid-feedback').hide();

  // Validate form
  const amount = parseFloat($('#ptokenAmount').val());

  if (isNaN(amount) || amount < 0 || amount > document.current_ptoken_total_available) {
    $('#ptokenAmount').addClass('is-invalid');
    $('#ptokenAmount ~ .invalid-feedback').show();
    return;
  }
  $('#ptokenAmount').removeClass('is-invalid');
  $('#ptokenAmount ~ .invalid-feedback').hide();


  if (!$('#ptokenTerms').is(':checked')) {
    $('#TOSText').addClass('is-invalid');
    $('#TOSText ~ .invalid-feedback').show();
    return;
  }
  $('#ptokenTerms').removeClass('is-invalid');
  $('#ptokenTerms ~ .invalid-feedback').hide();


  // Form is good, so continue with transaction
  buyPToken($('#ptokenAmount').val());
});

$(document).on('input', '#ptokenRedeemAmount', (event) => {
  event.preventDefault();
  const amount = $(event.target).val() === '' ? 0 : $(event.target).val(); // set to zero if field is empty

  $('#redeem-amount').text(parseFloat(amount));
});

$(document).on('input', '#ptokenAmount', (event) => {
  event.preventDefault();
  const amount = $(event.target).val() === '' ? 0 : $(event.target).val(); // set to zero if field is empty

  $('#ptokenCost').text(`${(document.current_ptoken_value * parseFloat(amount)).toFixed(2) || 0} ${purchaseTokenName}`);
  $('#buy-amount').text(amount);
});

$(document).on('click', '#submit_redeem_token', (event) => {
  event.preventDefault();

  // Hide existing validation errors
  $('#ptokenRedeemAmount').removeClass('is-invalid');
  $('#ptokenRedeemAmount ~ .invalid-feedback').hide();
  $('#ptokenRedeemDescription').removeClass('is-invalid');
  $('#ptokenRedeemDescription ~ .invalid-feedback').hide();
  $('#ptokenRedeemTerms').removeClass('is-invalid');
  $('#ptokenRedeemTerms ~ .invalid-feedback').hide();

  // Get form info
  const form = $('#ptokenRedeemForm')[0];
  const amountField = $(form.ptokenRedeemAmount);
  const tos = $(form.ptokenRedeemTerms);
  const redeem_amount = parseFloat(amountField.val());
  const redeem_description = $('#ptokenRedeemDescription').val();

  // Validate amount
  if (isNaN(redeem_amount) || redeem_amount <= 0) {
    $('#ptokenRedeemAmount').addClass('is-invalid');
    $('#ptokenRedeemAmount ~ .invalid-feedback').show();
    $('#ptokenRedeemAmount ~ .invalid-feedback').text(`Please enter a number between 0 and ${document.current_hodling} ${document.current_ptoken_symbol}`);
    return;
  } else if (document.current_hodling === 0) {
    $('#ptokenRedeemAmount').addClass('is-invalid');
    $('#ptokenRedeemAmount ~ .invalid-feedback').show();
    $('#ptokenRedeemAmount ~ .invalid-feedback').text(`You don't have ${document.current_ptoken_symbol} tokens`);
    return;
  } else if (redeem_amount > document.current_hodling) {
    $('#ptokenRedeemAmount').addClass('is-invalid');
    $('#ptokenRedeemAmount ~ .invalid-feedback').show();
    $('#ptokenRedeemAmount ~ .invalid-feedback').text(`You can't redeem more than ${document.current_hodling}  ${document.current_ptoken_symbol}`);
    return;
  }

  // Validate description
  if (redeem_description.length < 1) {
    $('#ptokenRedeemDescription').addClass('is-invalid');
    $('#ptokenRedeemDescription ~ .invalid-feedback').show();
    return;
  }

  // Validate terms
  if (!tos.prop('checked')) {
    event.stopPropagation();
    $('#TOSText').addClass('is-invalid');
    $('#TOSText ~ .invalid-feedback').show();
    return;
  }

  requestPtokenRedemption(redeem_amount, redeem_description);
});

function getTokenByName(name) {
  if (name === 'ETH') {
    return {
      addr: ETH_ADDRESS,
      name: 'ETH',
      decimals: 18,
      priority: 1
    };
  }
  var network = document.web3network;

  return tokens(network).filter(token => token.name === name)[0];
}

async function buyPToken(tokenAmount) {
  try {
    const network = checkWeb3();

    BN = web3.utils.BN;

    [user] = await web3.eth.getAccounts();
    const pToken = await new web3.eth.Contract(
      document.contxt.ptoken_abi,
      document.current_ptoken_address
    );
    const tokenDetails = getTokenByName('DAI');
    const tokenContract = new web3.eth.Contract(token_abi, tokenDetails.addr);
    // To properly handle decimal values, we first convert to Wei and then to a BN instance
    const token_value = new BN(web3.utils.toWei(String(document.current_ptoken_value)), 10);
    const amount = new BN(web3.utils.toWei(tokenAmount, 'ether'));
    // true value = token value * number of requested tokens
    // We then need to convert from Wei to "undo" the above conversion of token_value to Wei
    const true_value = new BN(web3.utils.fromWei(amount.mul(token_value)), 10);
    const allowance = new BN(await getAllowance(document.current_ptoken_address, tokenDetails.addr), 10);

    const waitingState = (state) => {
      indicateMetamaskPopup(!state);
      $('#submit_buy_token').prop('disabled', state);
      $('#close_buy_token').prop('disabled', state);
    };

    const purchasePToken = () => {
      waitingState(true);
      pToken.methods
        .purchase(amount.toString())
        // We hardcode gas limit otherwise web3's `estimateGas` is used and this will show the user
        // that their transaction will fail because the approval tx has not yet been confirmed
        .send({ from: user, gasLimit: '300000' })
        .on('transactionHash', async function(transactionHash) {

          _alert('Saving transaction. Please do not leave this page.', 'success', 5000);
          await purchase_ptoken(
            document.current_ptoken_id,
            tokenAmount,
            user,
            (new Date()).toISOString(),
            transactionHash,
            network,
            tokenDetails
          );
          console.log('Purchase saved as pending transaction in database');

          const successMsg = 'Congratulations, your token purchase was successful!';
          const errorMsg = 'Oops, something went wrong purchasing the token. Please try again or contact support@gitcoin.co';

          updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg);

          waitingState(false);
          $('#buyTokenModal').bootstrapModal('hide');
          $('#buy_ptoken_modal').bootstrapModal('show');
          $('#buy-amount').text(tokenAmount);
          const etherscanUrl = network === 'mainnet'
            ? `https://etherscan.io/tx/${transactionHash}`
            : `https://${network}.etherscan.io/tx/${transactionHash}`;

          $('#buy-tx').prop('href', etherscanUrl);
        }).on('error', (error, receipt) => {
          waitingState(false);
          handleError(error);
        });
    };


    // Check user token balance against token value
    console.log(`== user allowance balance: ${allowance}`);
    const userTokenBalance = await tokenContract.methods.balanceOf(user).call({ from: user });

    // Balance is too small, exit checkout flow
    console.log(`== user token balance: ${userTokenBalance}`);
    if (new BN(userTokenBalance, 10).lt(true_value)) {
      _alert(`Insufficient ${tokenDetails.name} balance to complete checkout`, 'error');
      return;
    }

    waitingState(true);
    indicateMetamaskPopup();
    if (allowance.lt(true_value)) {
      tokenContract.methods.approve(document.current_ptoken_address, true_value.toString())
        .send({from: user})
        .on('transactionHash', function(txHash) {
          indicateMetamaskPopup(true);
          purchasePToken();
        }).on('error', (error, receipt) => {
          handleError(error);
        });
    } else {
      purchasePToken();
    }
  } catch (error) {
    handleError(error);
  }
}

async function requestPtokenRedemption(tokenAmount, redemptionDescription) {
  try {
    const network = checkNetwork(); // no web3 transactions are needed to request redemption
    const response = await request_redemption(document.current_ptoken_id, tokenAmount, redemptionDescription, network);

    $('#redeemTokenModal').bootstrapModal('hide');
    $('#redeemTokenSuccessModal').bootstrapModal('show');
    await updatePTokenInfoOnPage(document.current_ptoken_id);
  } catch (err) {
    handleError(err);
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

/**
 * Waits for the provided transaction to be mined, and after mining triggers a database update.
 * Displays the provided success and error messages on success/failure
 */
async function updatePtokenStatusinDatabase(transactionHash, successMsg, errorMsg) {
  console.log('Waiting for transaction to be mined...');
  callFunctionWhenTransactionMined(transactionHash, async() => {
    console.log('Transaction mined, updating database...');
    const res = await update_ptokens(); // update all ptokens in DB

    if (res.status === 200) {
      _alert(successMsg, 'success');
      console.log(successMsg);
    } else {
      _alert(errorMsg, 'error');
      console.error(errorMsg);
    }

    await updatePTokenInfoOnPage(document.current_ptoken_id);
  });
}

const updatePTokenInfoOnPage = async() => {
  const userTokenBalance = await getPToken(document.current_ptoken_id);

  console.log(userTokenBalance);


  $('#ptoken-price').text(userTokenBalance.price);
  $('#available-ptokens').text(userTokenBalance.available_to_redeem);
  $('#amount-available').text(userTokenBalance.available);
  $('#purchase-counter').text(userTokenBalance.purchases);
  if (parseInt(userTokenBalance.available_to_redeem) > 0) {
    $('#redeemPToken').attr('disabled', false);
    $('#redeemPToken').css('cursor', 'pointer');
    $('#redeemPToken').css('pointer-events', 'auto');
  } else {
    $('#redeemPToken').attr('disabled', true);
    $('#redeemPToken').css('cursor', 'default');
    $('#redeemPToken').css('pointer-events', 'none');
  }


  document.current_ptoken_value = parseInt(userTokenBalance.price);
  document.current_ptoken_total_available = parseInt(userTokenBalance.available);
  document.current_hodling = parseInt(userTokenBalance.available_to_redeem);
};

$(document).ready(() => {
  const tokenId = document.current_ptoken_id;

  setInterval(async() => {
    await updatePTokenInfoOnPage(tokenId);
  }, 10000);
});
