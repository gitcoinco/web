var round = function(num, decimals) {
  return Math.round(num * 10 ** decimals) / 10 ** decimals;
};
var normalizeUsername = function(username) {
  if (username.indexOf('@') != 0) {
    return '@' + username;
  }
  return username;
};


$(document).ready(function($) {
  var random_id = function() {
    var id_num = Math.random().toString(9).substr(2, 3);
    var id_str = Math.random().toString(36).substr(2);

    return id_num + id_str;
  };

  $(document).on('blur', '#amount', function(event) {
    event.preventDefault();
    update_registry();
  });

  $(document).on('paste', '.username', function(event) {
    var self = $(this);

    setTimeout(function() {
      self.html(self.html().replace(/(<([^>]+)>)/ig, ''));
    }, 10);
  });
  

  $(document).on('click', '#close_bounty', function(event) {
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

  $(document).on('input', '.username', function(event) {
    event.preventDefault();
    var username = $(this).text();

    if (username == '' || username == '@') {
      $(this).addClass('error');
    } else {
      $(this).removeClass('error');
    }
    update_registry();
  });

  $(document).on('click', '.remove', function(event) {
    event.preventDefault();
    $(this).parents('tr').remove();
    $(this).focus();
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
      var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
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

  $('#acceptBounty').click(function(e) {
    e.preventDefault();
    
    if (!$('#terms').is(':checked')) {
      _alert('Please accept the TOS.', 'error');
      return;
    }
    if (!document.transactions.length) {
      _alert('You do not have any transactions to payout.  Please add payees to the form.', 'error');
      return;
    }

    sendTransaction(0);
  });


  var get_amount = function(percent) {
    var total_amount = $('#amount').val();

    return percent * 0.01 * total_amount;
  };

  var add_row = function() {
    var num_rows = $('#payout_table').find('tr').length;
    var percent = num_rows <= 1 ? 100 : '';
    var denomination = $('#token_name').text();
    var amount = get_amount(percent);
    var html = '<tr><td><div class=username contenteditable="true">@</div></td><td><div class="percent" contenteditable="true">' + percent + '</div></td><td><div><span class=amount>' + amount + '</span> <span class=denomination>' + denomination + '</span></div></td><td><a class=remove href=#>X</a></td></tr>';

    $('#payout_table').append(html);
    $(this).focus();
  };

  var get_total_cost = function() {
    var num_rows = $('#payout_table').find('tr').length;
    var total = 0;
    var i = 1;

    for (i = 1; i < num_rows; i += 1) {
      var $row = $('#payout_table').find('tr:nth-child(' + i + ')');
      var amount = parseFloat($row.find('.amount').text());
      var username = $row.find('.username').text();
      var is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';

      if (!is_error) {
        total += amount;
      }
    }
    return total;
  };

  var update_registry = function() {
    var num_rows = $('#payout_table').find('tr').length;
    var tc = round(get_total_cost(), 2);
    var denomination = $('#token_name').text();
    var original_amount = $('#original_amount').val();
    var net = round(original_amount - tc, 2);
    var close_bounty = $('#close_bounty').is(':checked');

    $('#total_cost').html(tc + ' ' + denomination);
    $('#total_net').html(net + ' ' + denomination);

    var transactions = [];

    first_transaction = {
      'id': 1,
      'type': 'cancel',
      'reason': 'Bounty Stake',
      'amount': '+' + original_amount + ' ' + denomination
    };

    var i = 0;

    if (close_bounty) {
      transactions.push(first_transaction);
      i += 1;
    }

    for (let j = i; j < num_rows; j += 1) {
      var $row = $('#payout_table').find('tr:nth-child(' + j + ')');
      var amount = parseFloat($row.find('.amount').text());
      var username = $row.find('.username').text();

      transaction = {
        'id': j + 1,
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

  $('document').ready(function() {
    add_row();
    update_registry();

    $('.add_another').click(add_row);

  });
});