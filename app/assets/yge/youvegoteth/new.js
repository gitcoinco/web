
window.onload = function() {
  var _click = function() {
    var num_batches = 1;

    if ($('batches')) {
      num_batches = parseInt($('batches').value);
    }
    var addresses = [];

    for (var i = 0; i < num_batches; i++) {
      var newAccount = document.Accounts.new('');
      var address = newAccount.address;
      var _private_key = newAccount.private;

      addresses[i] = {
        'address': address,
        'pk': _private_key
      };
    }
    localStorage.setItem('addresses', JSON.stringify(addresses));
    document.location.href = '/tip/send/2/';
    mixpanel.track('Tip Step 1 Click', {});
  };

  $('neweth').onclick = _click;
  if (getParam('batch')) {
    _alert('batch mode enabled', 'info');
    $('batches').style.display = 'block';
  }
  if (getParam('username')) {
    localStorage['username'] = getParam('username');
  }
};
