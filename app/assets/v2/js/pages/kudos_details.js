var cloneKudos = function(name, numClones) {
  console.log('name: ' + name);
  console.log('numClones: ' + numClones);

  var account = web3.eth.coinbase;
  var kudosContractInstance = web3.eth.contract(kudos_abi).at(kudos_address());

  kudosContractInstance.clone(name, numClones, {from: account, value: new web3.BigNumber(1000000000000000)}, function(error, txid) {
    console.log('txid:' + txid)
    return true;
  })
}

var getKudosById = function(kudosId) {
  $.get('/api/v0.1/kudos/' + kudosId, function(results, status) {
    return results
  })
}



$(document).ready(function() {
  kudos_levitate();
  console.log('here');
  let kudosId = window.location.pathname.split('/')[2];
  // let kudosId = $('#kudosId').text()
  // let kudosName = $('#kudosName').text()
  let kudosNumClonesAvailable = $('#kudosNumClonesAvailable').text()
  let kudosNumClonesAllowed = $('#kudosNumClonesAllowed').text()
  let numClones = 1;

  if (kudosNumClonesAvailable == 0) {
    $('#getKudos').attr('class', 'btn btn-gc-blue disabled').attr('aria-disabled', 'true');
    return;
  }

  $('#getKudos').click(function() {
    if (numClones > kudosNumClonesAvailable) {
      alert('Cannot make ' + numClones + ' clone(s).  ' + kudosNumClonesAvailable + ' clones available!');
      return;
    }

    $.get('/api/v0.1/kudos/' + kudosId, function(results, status) {
      let kudosName = results.name;
      cloneKudos(kudosName, numClones);
    })
  })

})


var kudos_levitate = function(){
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
          .fromTo(shadow, 1, { scale: 1, transformOrigin: 'center center', ease: Power1.easeInOut, yoyo: true, repeat: -1 }, { scale: 0.5, transformOrigin: 'center center', ease: Power1.easeInOut, yoyo: true, repeat: -1 },  'sapph')
     


  sparkleTl.to(twinkle1, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle')
           .to(twinkle2, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle+=0.3')
           .to(twinkle3, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle+=0.6')
           .to(twinkle4, 1, { scale: 0, transformOrigin: 'center center', ease: Power1.easeOut }, 'sparkle+=0.9')
           .to(twinkle1, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow')
           .to(twinkle2, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow+=0.3')
           .to(twinkle3, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow+=0.6')
           .to(twinkle4, 1, { scale: 1, transformOrigin: 'center center', ease: Elastic.easeOut }, 'sparkleshow+=0.9')

  sparkleTl.timeScale(2);
}

// $('#getKudos').click(function() {


// $(document).ready(function() {
//   let address = web3.eth.coinbase;
//   console.log(address);
//   $.get('/api/v0.1/kudos?lister=' + address, function(results, status) {
//     console.log(status)
//     console.log(results)
//     let numKudos = results.length;
//     results.forEach(renderKudos)
//     // renderKudos(results)
//   })
// })