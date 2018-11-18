$(document).ready(function() {

  var rotateKudos = function(){
    var cssSelector = anime({
      targets: '#kudosImg',
      easing: 'easeInOutQuart',
      rotate: 360 * 2,
      duration: 1000,
    });
  }
  var moveKudosToAvatar = function(){
    var target2 = $(".nav_avatar").offset();
    var target1 = $("#kudosImg").offset();


    var cssSelector = anime({
      targets: '#kudosImg',
      translateX: target2.left - target1.left,
      translateY: target2.top - target1.top,
      height: 10,
      loop: true,
      easing: 'easeInOutQuart',
      rotate: 360 * 2,
      duration: 3000,
    });
  }
  if($("#forwarding_address:visible").length == 0){
    moveKudosToAvatar();
  }

  $("#receive").click(function(){
    rotateKudos();
  });

  if (typeof web3 == 'undefined') {
    _alert({ message: gettext('You are not on a web3 browser.  Please switch to a web3 browser.') }, 'error');
    $('#receive').attr('disabled', 'disabled');
  }
  if (!$('#user').val()) {
    $('#receive').attr('disabled', 'disabled');
  }

  waitforWeb3(function() {
    if (document.web3network == 'locked') {
      _alert('Metamask not connected. <button id="metamask_connect" onclick="approve_metamask()">Click here to connect to metamask</button>', 'error');
    } else if (document.web3network != document.network) {
      _alert({ message: gettext('You are not on the right web3 network.  Please switch to ') + document.network }, 'error');
      $('#receive').attr('disabled', 'disabled');
    } else {
      $('#forwarding_address').val(web3.eth.coinbase);
    }
  });

});