window.addEventListener('load', function() {
  if (web3.currentProvider.isTrust) {
    $('#trust_label').show();
  } else {
    $('#metamask_label').show();
  }

  $(document).on('click', '#accordion-set-own-limit', function() {
    $('#metamask_context').toggle();
    if ($('#accordion-set-own-limit i').hasClass('fa-angle-down')) {
      $('#accordion-set-own-limit i').removeClass('fa-angle-down').addClass('fa-angle-up');
    } else {
      $('#accordion-set-own-limit i').removeClass('fa-angle-up').addClass('fa-angle-down');
    }
  });

  $(document).on('click', '#gas-section .recommended-prices', function() {
    var usdAmount = $(this).data('amount');
    var ethAmount = Math.round(1000000 * usdAmount / document.eth_usd_conv_rate) / 1000000;
    var gasPrice = Math.round(10 * ethAmount * Math.pow(10, 9) / gasLimit) / 10;

    $('#gas-section .recommended-prices').removeClass('active');
    $(this).addClass('active');
    $('#gas-usd').html('$' + usdAmount);
    $('#gas-eth').html(ethAmount + 'ETH');
    $('#gasPriceRecommended').val(gasPrice);
  });
});

