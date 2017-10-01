var abi = [{"inputs": [{"type": "address", "name": "_idx"}, {"type": "address", "name": "_to"}], "constant": false, "name": "claimTransfer", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": ""}], "constant": true, "name": "transfers", "outputs": [{"type": "bool", "name": "active"}, {"type": "uint256", "name": "amount"}, {"type": "uint256", "name": "developer_tip_pct"}, {"type": "bool", "name": "initialized"}, {"type": "uint256", "name": "expiration_time"}, {"type": "address", "name": "from"}, {"type": "address", "name": "owner"}, {"type": "address", "name": "erc20contract"}, {"type": "uint256", "name": "fee_amount"}], "payable": false, "type": "function"}, {"inputs": [{"type": "bool", "name": "_disableDeveloperTip"}, {"type": "address", "name": "_owner"}, {"type": "address", "name": "_contract"}, {"type": "uint256", "name": "_amount"}, {"type": "uint256", "name": "_fee_amount"}, {"type": "uint256", "name": "expires"}], "constant": false, "name": "newTransfer", "outputs": [], "payable": true, "type": "function"}, {"inputs": [{"type": "address", "name": "_idx"}], "constant": false, "name": "getTransferDetails", "outputs": [{"type": "bool", "name": ""}, {"type": "uint256", "name": ""}, {"type": "uint256", "name": ""}, {"type": "bool", "name": ""}, {"type": "uint256", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}, {"type": "address", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_idx"}], "constant": false, "name": "expireTransfer", "outputs": [], "payable": false, "type": "function"}, {"inputs": [], "type": "constructor", "payable": false}, {"payable": true, "type": "fallback"}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "uint256", "name": "amount"}, {"indexed": false, "type": "address", "name": "erc20contract"}, {"indexed": false, "type": "address", "name": "index"}], "type": "event", "name": "transferSubmitted", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_from"}, {"indexed": false, "type": "uint256", "name": "amount"}, {"indexed": false, "type": "address", "name": "erc20contract"}, {"indexed": false, "type": "address", "name": "index"}], "type": "event", "name": "transferExpired", "anonymous": false}, {"inputs": [{"indexed": false, "type": "address", "name": "_to"}, {"indexed": false, "type": "uint256", "name": "amount"}, {"indexed": false, "type": "address", "name": "erc20contract"}, {"indexed": false, "type": "address", "name": "index"}], "type": "event", "name": "transferClaimed", "anonymous": false}];
var tokenabi = [{"inputs": [{"type": "address", "name": "_spender"}, {"type": "uint256", "name": "_value"}], "constant": false, "name": "approve", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [], "constant": true, "name": "totalSupply", "outputs": [{"type": "uint256", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_from"}, {"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "name": "transferFrom", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}], "constant": true, "name": "balanceOf", "outputs": [{"type": "uint256", "name": "balance"}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "name": "transfer", "outputs": [{"type": "bool", "name": ""}], "payable": false, "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}, {"type": "address", "name": "_spender"}], "constant": true, "name": "allowance", "outputs": [{"type": "uint256", "name": "remaining"}], "payable": false, "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer", "anonymous": false}];

var getWarning = function(){
    var warning = "";
    if(network_id == 3){
        warning = "(Ropsten)";
    } else if(network_id == 9){
        warning = "(TestRPC)";
    }
    return warning;
};

function getParam(parameterName) {
    var result = null,
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
          tmp = item.split("=");
          if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    return result;
}

var setNetworkSelect = function(newNum){
    setTimeout(function(){
        if(!document.getElementById("network")){
            setNetworkSelect(newNum);
        } else {
            console.log(newNum);
            document.getElementById("network").selectedIndex = newNum;        
        }
    },100);
}
var setContractSelect = function(newNum){
    setTimeout(function(){
        if(!document.getElementById("contract")){
            setContractSelect();
        } else {
            document.getElementById("contract").selectedIndex = newNum;        
        }

    },100);
}

//figure out what network to point at
network_id=0; //mainnet
var etherscanDomain = 'etherscan.io';
if(getParam('network') != null || getParam('n') != null){
    var newNetwork = parseInt(getParam('network'));
    if(getParam('n')){
        newNetwork = parseInt(getParam('n'));
    }
    localStorage.setItem('network_id', newNetwork);
    network_id = newNetwork;
} else if(localStorage.getItem('network_id') != null){
    network_id = parseInt(localStorage.getItem('network_id'));
}

//default to latest contract, unless user has a link to receive.html where addres/key are specificed but contract verseion is not.
contract_revision=1;
setContractSelect(1);

if(network_id==9){
    //testrpc
    var contract_address = '0x852624f8b99431a354bf11543b10762fd3cdfae3'; 
    setNetworkSelect(2);
    etherscanDomain = 'localhost';
}
else if(network_id==3){
    //ropsten
    var contract_address = '0x0';
    contract_address = '0xb917e0f1fdebb89d37cbe053f59066a20b6794d6'; //ropsten v1
    etherscanDomain = 'ropsten.etherscan.io';
    setNetworkSelect(1);    
} else {
    //mainnet
    var contract_address = '0x0';
    contract_address = '0x8bcaadc84fd3bdea3cc5dd534cd85692a820a692'; //mainnet v1
    setNetworkSelect(0);
}
var contract = function(){
    return web3.eth.contract(abi).at(contract_address);
}
var token_contract = function(token_address){
    return web3.eth.contract(tokenabi).at(token_address);
}

var onNetworkChange = function(){
    var newNetwork = parseInt($("network").value);
    localStorage.setItem('network_id', newNetwork);
    document.location.href = document.location.href;
}


//background moving 
setTimeout(function () {

    var startX = null;
    var startY = null;
    var movementStrength = 25;
    var _height = 1000;
    var _width = 1000;
    var height = movementStrength / _height;
    var width = movementStrength / _width;
      $("yge").addEventListener("mousemove",function(e){
            var pageX = e.pageX - (_height / 2);
            var pageY = e.pageY - (_width / 2);
            var newvalueX = width * (pageX - startX) * -1 - 25;
            var newvalueY = height * (pageY - startY) * -1 - 50;
            if(!startX){
              startX = newvalueX;
            }
            if(!startY){
              startY = newvalueY;
            }
            $("yge").style.backgroundPosition =  (newvalueX - startX - 10)+"px     "+(newvalueY - startY - 10)+"px";
      });
});
