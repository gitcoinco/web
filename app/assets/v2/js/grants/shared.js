$(document).ready(function() {
  var params = {
    page: document.location.pathname
  };

  const listen_web3_1_changes = () => {
    web3.eth.getCoinbase().then(function(result) {
      show_error_banner(result);
      if (result) {
        web3.eth.getBalance(result, function(err, balance) {
          document.balance = balance;
        });
        web3.eth.net.getNetworkType(function(err, network) {
          currentNetwork(network);
        });
      } else {
        currentNetwork('locked');
      }
    });
  };

  setInterval(listen_web3_1_changes, 1000);

  const show_error_banner = (result) => {
    if ($('#grants_form').length) {
      var is_zero_balance_not_okay = document.location.href.indexOf('/faucet') == -1;

      if (typeof web3 == 'undefined') {
        $('#no_metamask_error').css('display', 'block');
        $('#zero_balance_error').css('display', 'none');
        $('#robot_error').removeClass('hidden');
        $('#grants_form').addClass('hidden');
        $('.submit_bounty .newsletter').addClass('hidden');
        $('#unlock_metamask_error').css('display', 'none');
        $('#connect_metamask_error').css('display', 'none');
        $('#no_issue_error').css('display', 'none');
        mixpanel_track_once('No Metamask Error', params);
      } else if (is_metamask_unlocked && !is_metamask_approved) {
        $('#connect_metamask_error').css('display', 'block');
        $('#unlock_metamask_error').css('display', 'none');
        $('#zero_balance_error').css('display', 'none');
        $('#no_metamask_error').css('display', 'none');
        $('#robot_error').removeClass('hidden');
        $('#grants_form').addClass('hidden');
        $('.submit_bounty .newsletter').addClass('hidden');
        $('#no_issue_error').css('display', 'none');
        mixpanel_track_once('Unlock Metamask Error', params);
      } else if (!result) {
        $('#unlock_metamask_error').css('display', 'block');
        $('#connect_metamask_error').css('display', 'none');
        $('#zero_balance_error').css('display', 'none');
        $('#no_metamask_error').css('display', 'none');
        $('#robot_error').removeClass('hidden');
        $('#grants_form').addClass('hidden');
        $('.submit_bounty .newsletter').addClass('hidden');
        $('#no_issue_error').css('display', 'none');
        mixpanel_track_once('Unlock Metamask Error', params);
      } else if (is_zero_balance_not_okay && document.balance == 0) {
        $('#zero_balance_error').css('display', 'block');
        $('#robot_error').removeClass('hidden');
        $('#grants_form').addClass('hidden');
        $('.submit_bounty .newsletter').addClass('hidden');
        $('#unlock_metamask_error').css('display', 'none');
        $('#connect_metamask_error').css('display', 'none');
        $('#no_metamask_error').css('display', 'none');
        $('#no_issue_error').css('display', 'none');
        mixpanel_track_once('Zero Balance Metamask Error', params);
      } else {
        $('#zero_balance_error').css('display', 'none');
        $('#unlock_metamask_error').css('display', 'none');
        $('#no_metamask_error').css('display', 'none');
        $('#connect_metamask_error').css('display', 'none');
        $('#no_issue_error').css('display', 'block');
        $('#robot_error').addClass('hidden');
        $('#grants_form').removeClass('hidden');
        $('.submit_bounty .newsletter').removeClass('hidden');
      }
    }
  };
});

// Waiting State screen
const enableWaitState = container => {
  $(container).hide();
  $('.interior .body').addClass('open');
  $('.interior .body').addClass('loading');
  $('.grant_waiting').show();
  waitingStateActive();
};
