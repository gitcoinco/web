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