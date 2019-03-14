var cloneKudos = function(name, numClones) {
  console.log('name: ' + name);
  console.log('numClones: ' + numClones);

  var account = web3.eth.coinbase;
  var kudosContractInstance = web3.eth.contract(kudos_abi).at(kudos_address());

  kudosContractInstance.clone(name, numClones, {from: account, value: new web3.BigNumber(1000000000000000)}, function(error, txid) {
    console.log('txid:' + txid);
    return true;
  });
};

var getKudosById = function(kudosId) {
  $.get('/api/v0.1/kudos/' + kudosId, function(results, status) {
    return results;
  });
};


$(document).ready(function() {
  // stop_kudos_levitate();
  // let kudosId = window.location.pathname.split('/')[2];
  // let kudosId = $('#kudosId').text()
  // let kudosName = $('#kudosName').text()
  let kudosNumClonesAvailable = parseInt($('#kudosNumClonesAvailable').text());
  let kudosNumClonesAllowed = parseInt($('#kudosNumClonesAllowed').text());
  let numClones = kudosNumClonesAvailable - kudosNumClonesAllowed;

  $('#kudos-image').hover(function() {
    start_kudos_levitate();
  }, function() {
    stop_kudos_levitate();
  });


  $('.kudos_levitate_container, #kudos-image').on('click', function() {

    pct_msg_should_be_shown = 0; // Disabled, *for now*.  I will convince people that
    // the Kudos should say something at some point :) - KO
    if (Math.random() < pct_msg_should_be_shown) {
      rotate_kudos_msg();
      $('.kudos_msg').css('display', 'block');
      setTimeout(function() {
        $('.kudos_msg').css('display', 'none');
      }, 1000);
    } else {
      $('#kudos-image').addClass('shake');
      setTimeout(function() {
        $('#kudos-image').removeClass('shake');
      }, 1000);
    }

  });

  if (kudosNumClonesAvailable == 0) {
    $('#getKudos').attr('class', 'btn btn-gc-blue disabled').attr('aria-disabled', 'true');
    return;
  }

  $('#getKudos').on('click', function() {
    if (numClones > kudosNumClonesAvailable) {
      _alert({ message: gettext('Cannot make ' + numClones + ' clone(s).  ' + kudosNumClonesAvailable + ' clones available!')}, 'error');
      return;
    }

    $.get('/api/v0.1/kudos/' + kudosId, function(results, status) {
      let kudosName = results.name;

      cloneKudos(kudosName, numClones);
    });
  });

});

var rotate_kudos_msg = function() {
  var messages = [
    [ 'Buy Me!', 'I\'m looking for a good home.' ],
    [ 'Please.. Choose me!', 'All I want is a good home.' ],
    [ 'Please.. Choose me!', "You don't know what it's like to live in the blockchain..." ],
    [ "It's ...", '... so lonely in here..' ],
    [ 'Am I the one?', '' ],
    [ 'Am I the one?', '(sad puppy dog eyes)' ],
    [ 'Who are you sending a kudos to?', "I bet I'll make them really happy!" ],
    [ 'Who are you sending a kudos to?', "I'm the one to make them happy!" ],
    [ 'I play nice with others.', '' ],
    [ "I'd look really good on a profile!", '' ],
    [ 'Who are you sending a kudos to?', "I'd look good on their profile.." ]
  ];
  var item = messages[Math.floor(Math.random() * messages.length)];
  var h1 = item[0];
  var p = item[1];

  $('.kudos_msg strong').text(h1);
  $('.kudos_msg p').text(p);
};


var start_kudos_levitate = function() {
  if (document.suppress_kudos_levitate_hover)
    return false;
  $('.kudos_levitate_container').css('display', 'block');
  var sapphire = document.getElementById('kudos-image');
  var shadow = document.getElementById('shadow');
  var sparkle1 = document.getElementById('sparkle1');
  var sparkle2 = document.getElementById('sparkle2');
  var sparkle3 = document.getElementById('sparkle3');
  var sparkle4 = document.getElementById('sparkle4');
  var twinkle1 = document.querySelectorAll('#sparkle1 > .st6, #sparkle1 > .st7');
  var twinkle2 = document.querySelectorAll('#sparkle2 > .st6, #sparkle2 > .st7');
  var twinkle3 = document.querySelectorAll('#sparkle3 > .st6, #sparkle3 > .st7');
  var twinkle4 = document.querySelectorAll('#sparkle4 > .st6, #sparkle4 > .st7');
  var sapphireTl = new TimelineLite();
  var sparkleTl = new TimelineLite({
    repeat: -1,
    yoyo: true,
    onComplete: function() {
      this.restart();
    }
  });

  sapphireTl.from(sapphire, 1, { y: '10px', ease: Power1.easeInOut, repeat: -1, yoyo: true }, 'sapph')
    .fromTo(shadow, 1, { scale: 1, transformOrigin: 'center center', ease: Power1.easeInOut, yoyo: true, repeat: -1 }, { scale: 0.5, transformOrigin: 'center center', ease: Power1.easeInOut, yoyo: true, repeat: -1 }, 'sapph');


  sparkleTl.to(twinkle1, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle')
    .to(twinkle2, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle+=0.3')
    .to(twinkle3, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle+=0.6')
    .to(twinkle4, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle+=0.9')
    .to(twinkle1, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow')
    .to(twinkle2, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow+=0.3')
    .to(twinkle3, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow+=0.6')
    .to(twinkle4, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow+=0.9');

  sparkleTl.timeScale(2);
};

var stop_kudos_levitate = function() {
  if (document.suppress_kudos_levitate_hover)
    return false;
  $('.kudos_levitate_container').css('display', 'none');
  TweenMax.killAll(false, true, false);

};

window.onclick = (event) => {
  if (event.target.id == 'share-modal') {
    $('#share-modal').css('display', 'none');
  }
};

$('#share-button').on('click', () => {
  $('#share-modal').css('display', 'block');
});

$('#share-modal .fa-times').on('click', () => {
  $('#share-modal').css('display', 'none');
});

$('#copyLink').on('click', () => {
  $('#shareLink').select();
  document.execCommand('copy');
  $('.tooltip-share .title-tooltip').html('Copied Link');
});
