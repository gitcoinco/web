// outside of document.ready to be in global scope
var compiledSubscription;
var compiledSplitter;
var contractVersion;

function grantCategoriesSelection(target, apiUrl) {
  $(target).select2({
    ajax: {
      url: apiUrl,
      dataType: 'json',
      processResults: function(data) {
        return {
          results: data.categories.map(category => {
            const name = category[0];
            const humanisedName = name.charAt(0).toUpperCase() + name.substring(1);

            const index = category[1];

            return {value: name, text: humanisedName, id: index};
          })
        };
      },
      cache: true
    },
    allowClear: true
  });
}

// Waiting State screen
var enableWaitState = container => {
  $(container).hide();
  $('.interior .body').addClass('open');
  $('.interior .body').addClass('loading');
  $('.grant_waiting').show();
  waitingStateActive();

};

var waitingStateActive = function() {
  $('.bg-container').show();
  $('.loading_img').addClass('waiting-state ');
  $('.waiting_room_entertainment').show();
  $('.issue-url').html('<a href="' + document.issueURL + '" target="_blank" rel="noopener noreferrer">' + document.issueURL + '</a>');
  const secondsBetweenQuoteChanges = 30;

  waitingRoomEntertainment();
  setInterval(waitingRoomEntertainment, secondsBetweenQuoteChanges * 1000);
  window.addEventListener('beforeunload', function(e) {
    if (!document.suppress_loading_leave_code) {
      var confirmationMessage = 'This change has NOT been saved. Please do not leave the page until the tx has confirmed!';

      (e || window.event).returnValue = confirmationMessage; // Gecko + IE
      return confirmationMessage; // Gecko + Webkit, Safari, Chrome etc.
    }
  });


};

/**
 * Disables button and throws alert with message if logged in user match username
 * and a different metamask address.
 * @param {string} username
 * @param {string} address
 * @param {string} button
 * @param {string} message
 */
const notifyOwnerAddressMismatch = (username, address, button, message) => {

  if (!web3 || !web3.eth || !username || !document.contxt.github_handle || !address) {
    return;
  }

  web3.eth.getAccounts((error, accounts) => {
    if (
      typeof accounts != 'undefined' &&
      document.contxt && document.contxt.github_handle == username &&
      accounts[0] && accounts[0].toLowerCase() != address.toLowerCase()
    ) {
      if ($(button).attr('disabled') != 'disabled') {
        $(button).attr('disabled', 'disabled');
        _alert({
          message: message
        }, 'error');
      }
    } else {
      $(button).removeAttr('disabled');
      $('.alert.error').remove();
    }
  });
};

const exceedFileSize = (file, size = 4000000) => {
  if (file.size > size)
    return true;
  return false;
};

const addGrantLogo = () => {
  $('#img-project').on('change', function() {
    if (checkFileSize(this, 4000000) === false) {
      _alert(`Grant Image should not exceed ${(4000000 / 1024 / 1024).toFixed(2)}MB`, 'error');
    } else {
      let reader = new FileReader();

      reader.onload = function(e) {
        $('#preview').attr('src', e.target.result);
        $('#preview').css('width', '100%');
        $('#js-drop span').hide();
        $('#js-drop input').css('visible', 'invisible');
        $('#js-drop').css('padding', 0);
      };
      reader.readAsDataURL(this.files[0]);
    }
  });
};

const show_error_banner = (result, web3_not_found) => {
  if ($('#grants_form').length) {
    var is_zero_balance_not_okay = document.location.href.indexOf('/faucet') == -1 && !document.suppress_faucet_solicitation;

    if (typeof web3 == 'undefined' || web3_not_found) {
      $('#no_metamask_error').css('display', 'block');
      $('#zero_balance_error').css('display', 'none');
      $('#grants_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
      $('.alpha-warning').addClass('hidden');
    } else if (is_metamask_unlocked && !is_metamask_approved) {
      $('#connect_metamask_error').css('display', 'block');
      $('#unlock_metamask_error').css('display', 'none');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#grants_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');
      $('.alpha-warning').addClass('hidden');
    } else if (!result) {
      $('#unlock_metamask_error').css('display', 'block');
      $('#connect_metamask_error').css('display', 'none');
      $('#zero_balance_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      // $('#robot_error').removeClass('hidden');
      $('#grants_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#no_issue_error').css('display', 'none');
      $('.alpha-warning').addClass('hidden');
    } else if (is_zero_balance_not_okay && document.balance == 0) {
      $('#zero_balance_error').css('display', 'block');
      $('#robot_error').removeClass('hidden');
      $('#grants_form').addClass('hidden');
      $('.submit_bounty .newsletter').addClass('hidden');
      $('#unlock_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'none');
      $('.alpha-warning').addClass('hidden');
    } else {
      $('#zero_balance_error').css('display', 'none');
      $('#unlock_metamask_error').css('display', 'none');
      $('#no_metamask_error').css('display', 'none');
      $('#connect_metamask_error').css('display', 'none');
      $('#no_issue_error').css('display', 'block');
      $('#robot_error').addClass('hidden');
      $('#grants_form').removeClass('hidden');
      $('.submit_bounty .newsletter').removeClass('hidden');
      $('.alpha-warning').removeClass('hidden');
    }
  }
};

$(document).ready(function() {

  contractVersion = $('#contract_version').val();

  if (contractVersion) {
    if (contractVersion == 0) {
      compiledSubscription = compiledSubscription0;
    } else if (contractVersion == 1) {
      compiledSubscription = compiledSubscription1;
    }
  }

  compiledSplitter = typeof compiledSplitter0 != 'undefined' ? compiledSplitter0 : null;

});


const getFormData = object => {
  const formData = new FormData();

  Object.keys(object).forEach(key => formData.append(key, object[key]));
  return formData;
};

/**
 * @notice Asks user to sign a message
 * @param {String} userAddress User's address
 * @param {String} baseMessage Message to sign
 * @returns The signature and the message
 */
const signMessage = async(userAddress, baseMessage) => {
  const ethersProvider = new ethers.providers.Web3Provider(provider); // ethers provider instance
  const signer = ethersProvider.getSigner(); // ethers signers
  const { chainId } = await ethersProvider.getNetwork(); // append chain ID if not mainnet to mitigate replay attack
  const message = chainId === 1 ? baseMessage : `${baseMessage}\n\nChain ID: ${chainId}`;

  // Get signature from user
  const isValidSignature = (sig) => ethers.utils.isHexString(sig) && sig.length === 132; // used to verify signature
  let signature = await signer.signMessage(message); // prompt to user is here, uses eth_sign

  // Fallback to personal_sign if eth_sign isn't supported (e.g. for Status and other wallets)
  if (!isValidSignature(signature)) {
    signature = await ethersProvider.send(
      'personal_sign',
      [ ethers.utils.hexlify(ethers.utils.toUtf8Bytes(message)), userAddress.toLowerCase() ]
    );
  }

  // Verify signature
  if (!isValidSignature(signature)) {
    throw new Error(`Invalid signature: ${signature}`);
  }

  return { signature, message };
};

/**
 * @notice Ingests a user's contributions into the database
 * @param {String[]} txHash Array of transaction hashes from the checkout. For standard checkout, this is an array of
 * length one. For zkSync checkout, this is an array with a unique transaction hash for each contribution
 * @param {String} userAddress User's address
 * @param {String} baseMessage Message to sign
 * @param {String} handle user to ingest under -- ignored unless you are a staff
 */
const postToDatabaseManualIngestion = async(txHash, userAddress, baseMessage, handle = undefined) => {
  // This method is used in two places:
  //   1. If called as fallback after checkout, we'll have both a txHash and userAddress parameter
  //   2. If called on the add-missing-contributions page, well only have one or the other
  //
  // Therefore we can detect if we're ingesting an L1 or L2 checkout as follows:
  //   - If the txHash parameter starts with 'sync', that indicates a zkSync transaction hash, so checkout type
  //     is eth_zksync
  //   - If the txHash parameter is an empty string, only an address was provided, and we manually ingest zkSync
  //     via address, so checkout_type is eth_zksync
  //   - Otherwise, we are ingesting for L1, so checkout_type is eth_std
  const checkout_type = txHash[0].startsWith('sync') || txHash[0] === '' ? 'eth_zksync' : 'eth_std';

  // We only want one of these two to be defined, since we only ingest one at a time
  txHash = checkout_type === 'eth_std' ? txHash[0] : ''; // txHash is always an array of hashes from checkout or empty if add-missing-contributions page
  userAddress = checkout_type === 'eth_zksync' ? userAddress : '';

  // Get user's signature to prevent ingesting arbitrary transactions under their own username, then ingest
  const { signature, message } = await signMessage(userAddress, baseMessage);
  const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const url = '/grants/ingest';
  const headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' };
  const network = document.web3network || 'mainnet';
  const payload = { csrfmiddlewaretoken, txHash, userAddress, signature, message, network, handle};
  const postParams = { method: 'POST', headers, body: new URLSearchParams(payload) };
  let json; // response

  // Send saveSubscription request
  try {
    _alert('Please be patient, as manual ingestion may take 1-2 minutes', 'info', '3000');
    const res = await fetch(url, postParams);

    json = await res.json();
    console.log('ingestion response: ', json);
    if (!json.success) {
      console.log('ingestion failed');
      throw new Error(`Your transactions could not be processed. Please visit ${window.location.host}/grants/add-missing-contributions to ensure your contributions are counted`);
    }
    _alert('Success!', 'success');
  } catch (err) {
    console.error(err);
    const message = `Your contribution was successful, but was not recognized by our database. Please visit ${window.location.host}/grants/add-missing-contributions to ensure your contributions are counted`;

    _alert(message, 'error');
    throw new Error(message);
  }
};