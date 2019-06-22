var _alert = function(msg, addClassName) {
  var existing_alerts = document.getElementsByClassName('alert_msg');

  for (var i = 0; i < existing_alerts.length; i++) {
    var top = parseInt(existing_alerts[i].style.top.replace('px', ''));

    if (isNaN(top)) {
      top = 0;
    }
    existing_alerts[i].style.top = top + 25 + 'px';
  }

  var para = document.createElement('p');

  para.className = 'alert_msg ' + addClassName;
  var element = document.body;

  element.appendChild(para);
  para.innerHTML = msg['message'];
  var callback = function() {
    para.parentNode.removeChild(para);
  };

  setTimeout(callback, 5000);
};
var metaMaskWarning = function() {
  if (typeof web3 == 'undefined' || !web3.currentProvider || !web3.currentProvider.isMetaMask) {
    if (typeof document.suppressweb3alert != 'undefined') {
      _alert({ message: gettext('You must install <a href=https://metamask.io/>Metamask</a> to use this tool.') }, 'info');
    }
    return true;
  } else if (is_metamask_unlocked && !is_metamask_approved) {
    _alert({ message: gettext('Please connect to Metamask.') }, 'info');
  } else if (web3.eth.accounts.length == 0) {
    _alert({ message: gettext('Please unlock Metamask.') }, 'info');
    return true;
  }
  return false;
};

setTimeout(metaMaskWarning, 1000);
var metaMaskWarningRecurr = function() {
  metaMaskWarning();
  setTimeout(metaMaskWarningRecurr, 5000);
};

setTimeout(metaMaskWarningRecurr, 6000);
