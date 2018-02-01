//stdbounties

var issueURL = 'https://github.com/ethereum/remix/issues/577'
localStorage[issueURL] = JSON.stringify({
    'timestamp': timestamp(),
    'dataHash': 'QmPM18xxTSYkZUEAf7PSkQZbS7pB4u86McXL549MJwh66Q',
    'issuer': web3.eth.coinbase,
    'txid': '0x926884369a8838bc766294bd52a84f2cad514ea82c159c0837ff923564b28cca',
});  
document.location.href = document.location.href 


//legacy gitcoin

localStorage['txid'] = '0x926884369a8838bc766294bd52a84f2cad514ea82c159c0837ff923564b28cca'
var issueURL = 'https://github.com/codesponsor/codesponsor/issues/59'
localStorage['dataHash'] = 'QmeDA7h2xZpXbnEwcpHkeZtqox6t4yrY77cpJEXze4uwDP';
localStorage['issuer'] = '0x28e21609ca8542ce5a363cbf339529204b043ede';
localStorage[issueURL] = timestamp();
document.location.href = document.location.href 

