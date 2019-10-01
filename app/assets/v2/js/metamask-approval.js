
var is_metamask_approved = is_metamask_approved || false;
var is_metamask_unlocked = is_metamask_unlocked || false;

window.addEventListener('load', checkProvider);

async function approve_metamask() {
  if (window.ethereum) {
    window.isWeb3Fired = true;
    window.web3 = new Web3(ethereum);
    try {

      await ethereum.enable();
      window.isWeb3Fired = false;
      is_metamask_approved = true;

    } catch (error) {
      _alert('Permission to connect to metamask rejected. Allow gitcoin to connect to metamask.', 'warning');
    }
  }
}
async function checkProvider() {
  var fortmatic = localStorage.getItem('fortmatic');

  if (!fortmatic && window.ethereum && window.ethereum._metamask) {
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
    window.removeEventListener('load', checkProvider);
    ask_metamask_connection();
  } else if (fortmatic) {
    window.isWeb3Fired = true;
    await ask_fortmatic_connection();
    window.isWeb3Fired = false;
  }
}

async function approve_fortmatic() {
  try {
    window.isWeb3Fired = true;
    $('.btn-fortmatic').text('Loading');
    $('.btn-fortmatic').addClass('btn-fortmatic--loading');
    await ask_fortmatic_connection();

    localStorage.setItem('fortmatic', web3.eth.coinbase);
    window.isWeb3Fired = false;
  } catch (error) {
    console.log(error);
    _alert('Permission to connect to fortmatic rejected. Allow gitcoin to connect to fortmatic.', 'warning');
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
    _alert('Provider not connected. <button class="metamask_connect" onclick="exec(approve_metamask,true)">Click here to connect to metamask</button> or <button id="fortmatic-provider" class="metamask_connect" onclick="exec(approve_fortmatic)">Click here to connect to Fortmatic</button>', 'error');
    $('.metamask_connect').css('background', 'none');
    $('.metamask_connect').css('color', 'white');
    $('.metamask_connect').css('border', '2px solid white');
    $('.metamask_connect').css('border-radius', '10px');
  }
}

async function exec(fn, isMetamask = false) {
  if (!isMetamask) {
    $('#fortmatic-provider').text('Loading');
    $('#fortmatic-provider').addClass('btn-fortmatic--loading');
  }
  await fn();
  window.location.reload();
}

async function ask_fortmatic_connection() {
  var fm = new Fortmatic(window.fortmatic_api_key);

  const web3 = new Web3(fm.getProvider());

  try {
    await web3.currentProvider.enable();
    window.web3 = web3;
    console.info('Fortmatic loaded');
    is_metamask_approved = true;
    WatchJS.watch(window.web3.currentProvider, 'isLoggedIn', function(prop, action, newvalue, oldvalue) {
      if (!newvalue) {
        localStorage.removeItem('fortmatic');
        window.location.reload();
      }
    });

  } catch (e) {
    console.log(e);
    _alert('Metamask not connected. <button id="metamask_connect" onclick="approve_metamask()" style="background: none; color: white; border: 2px solid white; border-radius: 10px;">Click here to connect to metamask</button>', 'error');
  }
}
