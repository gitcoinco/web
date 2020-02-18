// stdbounties
var issueURL = 'https://github.com/owocki/pytrader/issues/4';

web3.eth.getCoinbase(function(_, coinbase) {
  localStorage[issueURL] = JSON.stringify({
    'timestamp': timestamp(),
    'dataHash': null,
    'issuer': coinbase,
    'txid': '0xd2e45f7feea2e46d84e65ef3c1e5136ec7935252ba4b95dc4f170e067a9d9a75'
  });
});
document.location.href = document.location.href;

// legacy gitcoin
localStorage['txid'] = '0x926884369a8838bc766294bd52a84f2cad514ea82c159c0837ff923564b28cca';
var issueURL = 'https://github.com/codesponsor/codesponsor/issues/59';

localStorage['dataHash'] = 'QmeDA7h2xZpXbnEwcpHkeZtqox6t4yrY77cpJEXze4uwDP';
localStorage['issuer'] = '0x28e21609ca8542ce5a363cbf339529204b043ede';
localStorage[issueURL] = timestamp();
document.location.href = document.location.href;
