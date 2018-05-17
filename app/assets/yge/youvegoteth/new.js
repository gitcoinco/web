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
    var url_string = window.location.href;
    var url = new URL(url_string);
    var amount = url.searchParams.get('amount');
    var username = url.searchParams.get('username');
    var issueURL = url.searchParams.get('source');

    if (amount && username !== null) {
      localStorage.setItem('amount', amount);
      localStorage.setItem('username', username);
      localStorage.setItem('issueURL', issueURL);
    }
    localStorage.setItem('addresses', JSON.stringify(addresses));
    document.location.href = '/tip/send/2/';
    mixpanel.track('Tip Step 1 Click', {});
  };

  $('neweth').onclick = _click;
  if (getParam('batch')) {
    _alert({ message: gettext('batch mode enabled') }, 'info');
    $('batches').style.display = 'block';
  }
  if (getParam('username')) {
    localStorage['username'] = getParam('username');
  }
};
