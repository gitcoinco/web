var weiPerEther = 1000000000000000000;

// Make alias of docuemtn.getElementById -> $
function makeAlias(object, name) {
    var fn = object ? object[name] : null;
    if (typeof fn == 'undefined') return function () {}
    return function () {
        return fn.apply(object, arguments)
    }
}

var passphrase = 'youvegoteth';
var gasPrice = 1;
var gas = 100000 * 2;
var gasLimit = gas * 2;
var maxGas = 4468057;

// Make docuemtn.getElementById aliased by $
$ = makeAlias(document, 'getElementById');

// Create Accounts Object
if(Accounts){
  var Accounts = new Accounts();

  // Set web3 provider
  var host = ''
  if(network_id==9){
      host = "http://localhost:8545"; //testrpc
  }
  else if(network_id==3){
      host = 'https://ropsten.infura.io/'; //ropsten
  } else {
      host = 'https://mainnet.infura.io/'; //mainnet
  }
  var provider = new HookedWeb3Provider({
    host: host,
    transaction_signer: Accounts
  });
  web3.setProvider(provider);

  // Extend the web3 object
  Accounts.log = function(msg){console.log(msg);};

}
