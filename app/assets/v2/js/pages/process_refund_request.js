$(document).ready(function() {

  load_tokens();
  $('#rejectRefund').prop('disabled', true);

  $('#reject_comments').on('change keyup paste', function() {
    if ($(this).val().length > 0)
      $('#rejectRefund').prop('disabled', false);
    else
      $('#rejectRefund').prop('disabled', true);
  });

  $('#rejectRefund').on('click', function(e) {
    e.preventDefault();
    const data = {
      'comment': $('#reject_comments').val()
    };

    handleRequest(data);
  });

  $('#approveRefund').on('click', function(e) {
    e.preventDefault();
    $('#approveRefund').attr('disabled', 'disabled');

    $('#loadingImg').show();
    const from = web3.eth.coinbase;
    const to = $('#destination-addr').html();
    const amount = parseFloat($('#amount').html());
    const token = $('#token').html();
    const gasPrice = web3.toHex(document.gas_price * Math.pow(10, 9));

    console.log(from, 'from -> to', to);
    if (token == 'ETH') {
      web3.eth.sendTransaction({
        from: from,
        to: to,
        value: web3.toWei(amount, 'ether'),
        gasPrice: gasPrice
      }, function(error, txnId) {
        if (error) {
          console.log ('Unable to refund bounty fee. Please try again.', error);
          $('#errResponse').show();
          $('#loadingImg').hide();
        } else {
          $('#sucessResponse').show();
          $('#loadingImg').hide();
          console.log('transaction', txnId);
          const data = {
            txnId: txnId,
            fulfill: true
          };

          handleRequest(data);
        }
      });
    } else {
      // ERC 20 token
      const _token = tokenNameToDetails(document.web3network, token);
      const amountInWei = amount * 1.0 * Math.pow(10, _token.decimals);
      const token_contract = web3.eth.contract(token_abi).at(_token.addr);

      token_contract.transfer(to, amountInWei, { gasPrice: gasPrice },
        function(error, txnId) {
          if (error) {
            console.log ('Unable to refund bounty fee. Please try again.', error);
            $('#errResponse').show();
            $('#loadingImg').hide();
          } else {
            $('#sucessResponse').show();
            $('#loadingImg').hide();
            console.log('transaction', txnId);
            const data = {
              txnId: txnId,
              fulfill: true
            };

            handleRequest(data);
          }
        }
      );
    }

  });
});


const handleRequest = (data) => {
  let csrftoken = $("input[name='csrfmiddlewaretoken']").val();

  $.ajax({
    type: 'post',
    url: '',
    data: data,
    headers: {'X-CSRFToken': csrftoken},
    success: () => {
      if (data.comment)
        alert('Request Reject. You may now close this window');
      else
        alert('Request Processed. You may now close this window');
    },
    error: () => {
      _alert({ message: 'Something went wrong submitting your request. Please try again.'}, 'error');
    }
  });
};