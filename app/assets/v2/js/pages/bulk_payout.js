const round = function(num, decimals) {
  return Math.round(num * 10 ** decimals) / 10 ** decimals;
};

const normalizeUsername = function(username) {
  if (username.indexOf('@') != 0) {
    return '@' + username;
  }
  return username;
};

$(document).ready(function($) {

  $(document).on('blur', '#amount', function(event) {
    event.preventDefault();
    update_registry();
  });

  $(document).on('input', '.percent', function(event) {
    event.preventDefault();
    var percent = $(this).text();
    var is_error = !$.isNumeric(percent) || percent < 0;

    if (is_error) {
      $(this).addClass('error');
      $(this).parents('tr').find('.amount').text(0);
    } else {
      $(this).removeClass('error');
      var decimals = 3;
      var amount = round(get_amount(percent), decimals);

      $(this).parents('tr').find('.amount').text(amount);
    }
    update_registry();
  });

  $(document).on('click', '.remove', function(event) {
    event.preventDefault();
    $(this).parents('tr').remove();
    $(this).focus();
    update_registry();
  });

  var sendTransaction = function(i) {

    var transaction = document.transactions[i];

    if (!transaction) {
      // msg
      _alert('All transactions have been sent.  Your bounty is now paid out.', 'info');

      // show green checkmark
      $('#success_container').css('display', 'block');
      $('.row.content').css('display', 'none');

      return;
    }
    $('.entry').removeClass('active');
    $('.entry_' + transaction['id']).addClass('active');

    // cancel bounty
    if (transaction['type'] == 'cancel') {
      var callback = function(error, txid) {
        if (error) {
          _alert({ message: error }, 'error');
        } else {
          var url = 'https://' + etherscanDomain() + '/tx/' + txid;
          var msg = 'This tx has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

          // send msg to frontend
          _alert(msg, 'info');
          sendTransaction(i + 1);

          // tell frontend that this issue has a pending tx
          localStorage[$('#issueURL').val()] = JSON.stringify({
            timestamp: timestamp(),
            dataHash: null,
            issuer: web3.eth.coinbase,
            txid: txid
          });
        }
      };

      const contract_version = $('input[name=contract_version]').val();
      var bounty = web3.eth.contract(getBountyABI(contract_version)).
        at(bounty_address(contract_version));
      var gas_dict = { gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9)) };

      bounty.killBounty(
        $('#standard_bounties_id').val(),
        gas_dict,
        callback
      );

    } else {
      // get form data
      var email = '';
      var github_url = $('#issueURL').val();
      var from_name = document.contxt['github_handle'];
      var username = transaction['data']['to'];
      var amountInEth = transaction['data']['amount'];
      var comments_priv = '';
      var comments_public = '';
      var from_email = '';
      var accept_tos = $('#terms').is(':checked');
      var tokenAddress = transaction['data']['token_address'];
      var expires = 9999999999;

      var success_callback = function(txid) {
        var url = 'https://' + etherscanDomain() + '/tx/' + txid;
        var msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        // send msg to frontend
        _alert(msg, 'info');

        // text transaction
        sendTransaction(i + 1);
      };
      var failure_callback = function() {
        // do nothing
        $.noop();
      };

      return sendTip(email, github_url, from_name, username, amountInEth, comments_public, comments_priv, from_email, accept_tos, tokenAddress, expires, success_callback, failure_callback, false);
    }
  };

  $('#acceptBounty').on('click', function(e) {
    e.preventDefault();

    if (!$('#terms').is(':checked')) {
      _alert('Please accept the TOS.', 'error');
      return;
    }
    if (typeof document.transactions == 'undefined' || !document.transactions.length) {
      _alert('You do not have any transactions to payout.  Please add payees to the form.', 'error');
      return;
    }
    var usernames = $('.username-search');

    for (var i = 0; i < usernames.length; i++) {
      var username = usernames[i].textContent.trim();

      if (username === null || username === '' || username === '@') {
        _alert('Please provide a valid recipient Github username', 'error');
        return;
      }
    }
    sendTransaction(0);
  });


  var get_amount = function(percent) {
    var total_amount = $('#amount').val();

    return percent * 0.01 * total_amount;
  };

  var add_row = function() {
    var num_rows = $('#payout_table tbody').find('tr').length;
    var percent = num_rows <= 1 ? 100 : '';
    var denomination = $('#token_name').text();
    var amount = get_amount(percent);
    var html = `
      <tr>
        <td class="pl-0 pb-0">
          <div class="pl-0">
            <select onchange="update_registry()" class="username-search custom-select w-100 ml-auto mr-auto"></select>
          </div>
        </td>
        <td class="pb-0"><div class="percent" contenteditable="true">` + percent + `</div></td>
        <td class="pb-0"><div class="amount"><span class=amount>` + amount + '</span> <span class=denomination>' + denomination + `</span></div></td>
        <td class="pb-0"><a class=remove href=#><i class="fas fa-times mt-2"></i></a>
        </td>
      </tr>`;

    $('#payout_table tbody').append(html);
    userSearch('.username-search:last', true);
    $(this).focus();
  };

  $('document').ready(function() {
    add_row();
    update_registry();

    $('.add_another').on('click', function() {
      add_row();
    });
  });
});

var get_total_cost = function() {
  var rows = $('#payout_table tbody tr');
  var total = 0;

  for (i = 0; i < rows.length; i += 1) {
    var $rows = $(rows[i]);
    var amount = parseFloat($rows.find('.amount').text());
    var username = $rows.find('.username-search').text();
    var is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';

    if (!is_error) {
      total += amount;
    }
  }
  return total;
};

var update_registry = function(coinbase) {

  if (!coinbase) {
    web3.eth.getCoinbase(function(err, result) {
      update_registry(result);
    });
    return;
  }
  
  var num_rows = $('#payout_table tbody').find('tr').length;
  var tc = round(get_total_cost(), 2);
  var denomination = $('#token_name').text();
  var original_amount = $('#original_amount').val();
  var net = round(original_amount - tc, 2);
  var over = round((original_amount - get_total_cost()) * -1, 4);
  var addr = coinbase.substring(38);
  var pay_with_bounty = $('#pay_with_bounty').is(':checked');
  
  $('#total_cost').html(tc + ' ' + denomination);

  let transactions = [];
  
  first_transaction = {
    'id': 0,
    'type': 'cancel',
    'reason': 'Bounty cancellation and refund.',
    'amount': '+' + original_amount + ' ' + denomination
  };

  if (over > 0 && pay_with_bounty) {
    $('#total_net').html(net + ' ' + denomination);
    $('.overageAlert').css('display', 'inline-block');
    $('.overagePreview').css('display', 'inline-block');
    $('#total_overage').html(over + ' ' + denomination);
    $('#address_ending').html(addr + ' ');
    $('#preview_ending').html(addr + ' ');
    $('#preview_overage').html(over + ' ' + denomination);
    $('.tipAlert').css('display', 'none');
    $('.asyncAlert').css('display', 'none');
    $('.tipPreview').css('display', 'none');
    transactions.push(first_transaction);
  } else if (pay_with_bounty) {
    $('#total_net').html(net + ' ' + denomination);
    $('.overageAlert').css('display', 'none');
    $('.overagePreview').css('display', 'none');
    $('.tipAlert').css('display', 'none');
    $('.asyncAlert').css('display', 'none');
    $('.tipPreview').css('display', 'none');
    transactions.push(first_transaction);
  } else {
    $('#total_net').html(tc + ' ' + denomination);
    $('.tipAlert').css('display', 'inline-block');
    $('.asyncAlert').css('display', 'inline-block');
    $('.tipPreview').css('display', 'inline-block');
    $('#total_tip_overage').html(tc + ' ' + denomination);
    $('#address_tip_ending').html(addr + ' ');
    $('#preview_tip_ending').html(addr + ' ');
    $('#preview_tip_overage').html(tc + ' ' + denomination);
    $('.overageAlert').css('display', 'none');
    $('.overagePreview').css('display', 'none');
  }

  for (let j = 1; j <= num_rows; j++) {

    var $row = $('#payout_table tbody').find('tr:nth-child(' + j + ')');
    var amount = parseFloat($row.find('.amount').text());
    var username = $row.find('.username-search').text();

    if (username == '')
      return;

    transaction = {
      'id': j,
      'type': 'tip',
      'reason': 'Payment to ' + normalizeUsername(username),
      'amount': '-' + amount + ' ' + denomination,
      'data': {
        'to': username,
        'amount': amount,
        'denomination': denomination,
        'token_address': $('#token_address').val()
      }
    };

    var is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';

    if (!is_error)
      transactions.push(transaction);
  }

  // paint on screen
  $('#transaction_registry tr.entry').remove();
  var k = 0;

  for (k = 0; k < transactions.length; k += 1) {
    var trans = transactions[k];
    var html = "<tr class='entry entry_" + trans['id'] + "'><td>" + trans['id'] + '</td><td>' + trans['amount'] + '</td><td>' + trans['reason'] + '</td></tr>';

    $('#transaction_registry').append(html);
  }

  document.transactions = transactions;
};
