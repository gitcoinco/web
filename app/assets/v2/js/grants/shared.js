// outside of document.ready to be in global scope
var compiledSubscription;
var compiledSplitter;
var contractVersion;

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
  if (!web3 || !web3.eth)
    return;
  web3.eth.getAccounts((error, accounts) => {
    if (document.contxt.github_handle == username && accounts[0] &&
        accounts[0] != address) {
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
    var is_zero_balance_not_okay = document.location.href.indexOf('/faucet') == -1;

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

  compiledSplitter = compiledSplitter0 ? compiledSplitter0 : null;

  const listen_web3_1_changes = () => {
    if (typeof web3 == 'undefined' || typeof web3.eth.getCoinbase() == 'undefined') {
      return;
    }
    web3.eth.getCoinbase().then(function(result) {
      show_error_banner(result);
      if (result) {
        web3.eth.getBalance(result, function(err, balance) {
          document.balance = balance;
        });

        web3.eth.net.getId((err, network) => {
          currentNetwork(getNetwork(network));
        });

      } else {
        currentNetwork('locked');
      }
    }).catch(err => {
      show_error_banner(null, true);
    });
  };

  setInterval(listen_web3_1_changes, 1000);

});
