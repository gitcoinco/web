var weiPerEther = 1000000000000000000;
var gasPrice = 1;
var gas = 100000 * 2;
var gasLimit = gas * 2;
var maxGas = 4468057;
var recommendGas = 448057;

// Make alias of docuemtn.getElementById -> $
function makeAlias(object, name) {
    var fn = object ? object[name] : null;
    if (typeof fn == 'undefined') return function () {}
    return function () {
        return fn.apply(object, arguments)
    }
}

// Make docuemtn.getElementById aliased by $
$ = makeAlias(document, 'getElementById');

// Create Accounts Object
waitforWeb3(function(){
  if(Accounts){
    // Set web3 provider
    var host = ''
    if(document.web3network=='custom network'){
        host = "http://localhost:8545"; //testrpc
    }
    else if(document.web3network=='ropsten'){
        host = 'https://ropsten.infura.io/'; //ropsten
    } else {
        host = 'https://mainnet.infura.io/'; //mainnet
    }
    var provider = new HookedWeb3Provider({
      host: host,
      transaction_signer: document.Accounts
    });
    web3.setProvider(provider);


  }
});


if(Accounts){
var Accounts = new Accounts();

// Extend the web3 object
Accounts.log = function(msg){console.log(msg);};

}
document.Accounts = Accounts;