var cloneKudos = function(name, numClones) {
  if (numClones == undefined) {
    numClones = 1;
  }
  console.log('numClones: ' + numClones);
  var account = web3.eth.coinbase;
  var kudosContractInstance = web3.eth.contract(kudos_abi).at(kudos_address());

  // kudosContractInstance.clone(name, numClones, {from: account, value: new web3.BigNumber(1000000000000000)}, function(error, txid) {
  //   console.log('txid:' + txid)
  //   return true;
  // })
}



$(document).ready(function() {
  $('#getKudos').click(function() {
    cloneKudos();
  })
})