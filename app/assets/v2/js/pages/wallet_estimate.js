window.addEventListener('load', function() {
  if (web3.currentProvider.isTrust) {
    $('#trust_label').show();
  } else {
    $('#metamask_label').show();
  }
});