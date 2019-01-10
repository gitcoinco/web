function signMsgAndCreateSubdomain(message, from) {
  var msg = web3.toHex(message);
  var params = [ msg, from ];
  var method = 'personal_sign';

  web3.currentProvider.sendAsync({
    method,
    params,
    from
  }, function(err, result) {
    if (err)
      return console.error(err);
    if (result.error)
      return console.error(result.error);
    $.post('', { 'signedMsg': result.result, 'signer': from }, function(data) {
      _alert(data.msg);
      location.reload();
    });
  });
}

