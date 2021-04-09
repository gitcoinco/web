/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
// load_tokens_from_network('mainnet');
load_tokens();

$(document).ready(function() {
  // avoid multiple submissions
  $('#coinbase, #token_name, #token_address, #contract_name, #txid').val('');

  $('.js-select2').each(function() {
    $(this).select2();
  });
  // removes tooltip
  $('select').on('change', function(evt) {
    $('.select2-selection__rendered').removeAttr('title');
  });

  $('input[type=submit]').on('click', function(e) {
    // acutally submit form if data is present
    if ($('#network').val()) {
      return;
    }
    $(this).prop('disabled', true);

    // form
    var token_address = $('select[name=denomination]').val();
    var contract_address = bounty_address();
    var contract_name = $('select[name=contract] option:selected').text().trim();
    var token_name = $('select[name=denomination] option:selected').text().trim();

    // validation
    if (token_address == '0x0000000000000000000000000000000000000000') {
      _alert('You already are approved for this token');
      e.preventDefault();
      $(this).prop('disabled', false);
      return;
    }
    if (!web3 || typeof web3 == 'undefined') {
      _alert('You are not connected to a web3 wallet.  Please unlock metamask (or web3 wallet equivilent), set to mainnet, and connect to gitcoin on the mainnet (settings > connections).', 'danger');
      $(this).prop('disabled', false);
      return;
    }

    e.preventDefault();
    // actual approval
    var token_contract = new web3.eth.Contract(token_abi, token_address);
    var to = contract_address;


    token_contract.methods.allowance(selectedAccount, to).call({from: selectedAccount}, function(error, result) {
      if (error || Number(result) == 0) {
        var amount = 10 * 18 * 9999999999999999999999999999999999999999999999999999; // uint256

        _alert('Waiting the transaction.', 'success');
        indicateMetamaskPopup();
        token_contract.methods.approve(
          to,
          new web3.utils.BN(String(amount)).toNumber()
        ).send({
          from: selectedAccount,
          value: new web3.utils.BN(0),
          gasPrice: web3.utils.toHex(document.gas_price * Math.pow(10, 9))
        }).then((result) => {
          indicateMetamaskPopup(true);
          if (error) {
            $('input[type=submit]').prop('disabled', false);
            _alert('Token request denied - no permission for this token');
            return;
          }
          var tx = result.transactionHash;

          $('#coinbase').val(selectedAccount);
          $('#token_name').val(token_name);
          $('#token_address').val(token_address);
          $('#contract_name').val(contract_name);
          $('#network').val(document.web3network);
          $('#txid').val(tx);
          $('input[type=submit]').click();
          $('input[type=submit]').prop('disabled', false);
        }).catch(err => {
          console.log(err);
          $('input[type=submit]').prop('disabled', false);
        });
      } else {
        _alert('You have already approved this token for this contract');
        $('input[type=submit]').prop('disabled', false);
      }
    });


  });
});
