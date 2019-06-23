
var is_metamask_approved = is_metamask_approved || false;
var is_metamask_unlocked = is_metamask_unlocked || false;

async function metamaskApproval() {
  if (window.ethereum && window.ethereum._metamask) {
    window.web3 = new Web3(ethereum);
    is_metamask_approved = await window.ethereum._metamask.isApproved();
    is_metamask_unlocked = await window.ethereum._metamask.isUnlocked();

    try {
      if (is_metamask_unlocked && is_metamask_approved) {
        var start_time = ((new Date()).getTime() / 1000);

        await ethereum.enable();
        var now_time = ((new Date()).getTime() / 1000);
        var did_request_and_user_respond = (now_time - start_time) > 1.0;

        if (did_request_and_user_respond) {
          document.location.reload();
        }
      }
    } catch (error) {
      _alert('Permission to connect to metamask rejected. Allow gitcoin to connect to metamask.', 'warning');
    }
  }
  ask_metamask_connection();
}

window.addEventListener('load', metamaskApproval);

async function approve_metamask() {
  try {
    var start_time = ((new Date()).getTime() / 1000);

    await ethereum.enable();
    var now_time = ((new Date()).getTime() / 1000);
    var did_request_and_user_respond = (now_time - start_time) > 1.0;

    if (did_request_and_user_respond) {
      document.location.reload();
    }
    is_metamask_approved = true;
  } catch (error) {
    _alert('Permission to connect to metamask rejected. Allow gitcoin to connect to metamask.', 'warning');
  }
}

function ask_metamask_connection() {
  var page_url = $(location).attr('pathname');

  shown_on = [ '/tip/send/2', '/kudos/send', '/ens' ];
  var len = page_url.length - 1;
  
  if (page_url.lastIndexOf('/') === len) {
    page_url = page_url.substring(0, len);
  }
  if ($.inArray(page_url, shown_on) != -1 && !is_metamask_approved) {
    _alert('Metamask not connected. <button id="metamask_connect" onclick="approve_metamask()">Click here to connect to metamask</button>', 'error');
    $('#metamask_connect').css('background', 'none');
    $('#metamask_connect').css('color', 'white');
    $('#metamask_connect').css('border', '2px solid white');
    $('#metamask_connect').css('border-radius', '10px');
  }
}
