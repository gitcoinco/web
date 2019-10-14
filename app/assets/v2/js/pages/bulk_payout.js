const rateUser = (elem) => {
  let userSelected = $(elem).select2('data')[0].text;

  $(elem).parents('.new-user').next().find('[data-open-rating]').data('openUsername', userSelected.trim());
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


  $(document).on('click', '.toggleType', function(event) {
    event.preventDefault();
    if ($(this).data('type') == 'no') {
      $(this).html('(%)');
      $(this).data('type', 'pct');
    } else {
      $(this).html('(#)');
      $(this).data('type', 'no');
    }
    $('.input_amount').trigger('input');
  });


  $(document).on('input', '.input_amount', function(event) {
    event.preventDefault();
    var input_amount = $(this).text();
    var is_error = !$.isNumeric(input_amount) || input_amount < 0;

    if (is_error) {
      $(this).addClass('error');
      $(this).parents('tr').find('.amount').text(0);
    } else {
      $(this).removeClass('error');
      var decimals = 3;
      var amount = $('.toggleType').data('type') == 'no' ? input_amount : round(get_amount(input_amount), decimals);

      $(this).parents('tr').find('.amount').text(amount);
    }
    update_registry();
  });

  $(document).on('click', '.remove', function(event) {
    event.preventDefault();
    $(this).parents('.new-user').next('tr').remove();
    $(this).parents('.new-user').remove();
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
        indicateMetamaskPopup(true);
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

      indicateMetamaskPopup();
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
    getFulfillers();
    update_registry();

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

  $('document').ready(function() {
    add_row();
    update_registry();

    $('.add_another').on('click', function() {
      add_row();
    });

  });
});

var get_amount = function(percent) {
  var total_amount = $('#amount').val();

  return percent * 0.01 * total_amount;
};

var add_row = function() {
  let bountyId = $('#bountyId').val();
  var num_rows = $('#payout_table tbody').find('tr.new-user').length;
  var input_amount = num_rows <= 1 ? 100 : '';
  var denomination = $('#token_name').text();
  var amount = get_amount(input_amount);
  let username = '';
  var html = `
    <tr class="new-user">
      <td class="pl-0 pb-0">
        <div class="pl-0">
          <select onchange="update_registry()" class="username-search custom-select w-100 ml-auto mr-auto"></select>
        </div>
      </td>
      <td class="pb-0"><div class="input_amount" contenteditable="true">${input_amount}</div></td>
      <td class="pb-0"><div class="amount"><span class=amount>${amount}</span> <span class=denomination>${denomination}</span></div></td>
      <td class="pb-0"><a class=remove href=#><i class="fas fa-times mt-2"></i></a>
      </td>
    </tr>
    <tr>
      <td>
        <fieldset class="" id="${num_rows}-${bountyId}" >
          <label for="" class="form__label">Rate contributor</label>
          <div class="rating" data-open-rating=${bountyId} data-open-username=${username}>
            <input type="radio" id="${num_rows}-${bountyId}-5" name="${num_rows}${bountyId}" value="5" />
            <label class ="rating-star full" for="${num_rows}-${bountyId}-5" data-toggle="tooltip" title="It was great - 5 stars"></label>
            <input type="radio" id="${num_rows}-${bountyId}-4" name="${num_rows}${bountyId}" value="4" />
            <label class ="rating-star full" for="${num_rows}-${bountyId}-4" data-toggle="tooltip" title="It was good - 4 stars"></label>
            <input type="radio" id="${num_rows}-${bountyId}-3" name="${num_rows}${bountyId}" value="3" />
            <label class ="rating-star full" for="${num_rows}-${bountyId}-3" data-toggle="tooltip" title="It was okay - 3 stars"></label>
            <input type="radio" id="${num_rows}-${bountyId}-2" name="${num_rows}${bountyId}" value="2" />
            <label class ="rating-star full" for="${num_rows}-${bountyId}-2" data-toggle="tooltip" title="It was bad - 2 stars"></label>
            <input type="radio" id="${num_rows}-${bountyId}-1" name="${num_rows}${bountyId}" value="1" />
            <label class ="rating-star full" for="${num_rows}-${bountyId}-1" data-toggle="tooltip" title="It was terrible - 1 star"></label>
          </div>
        </fieldset>
      </td>
    </tr>`;

  $('#payout_table tbody').append(html);
  userSearch('.username-search:last', true);
  $('body .username-search').each(function() {
    $(this).on('select2:select', event => {
      rateUser($(this));
    });
  });

  $(this).focus();
};

var get_total_cost = function() {
  var rows = $('#payout_table tbody tr.new-user');
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

  var num_rows = $('#payout_table tbody').find('tr.new-user').length;
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

  for (let j = 0; j <= num_rows; j++) {

    var $row = $('#payout_table tbody').find('tr:nth-child(' + ((j * 2) + 1) + ')');
    var amount = parseFloat($row.find('.amount').text());
    var username = $row.find('.username-search').text();

    if (username == '')
      continue;

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

/**
 * stores fulfillers in sessionStorage on
 * triggering advanced payout
 */
const getFulfillers = () => {
  let fulfillers = [];
  const users = $('.new-user option');

  for (let i = 0; i < users.length; i++) {
    fulfillers.push($('.new-user option')[i].innerHTML);
  }
  sessionStorage['fulfillers'] = fulfillers;
  sessionStorage['bountyId'] = $('#bountyId').val();
};

$(document).on('click', '.user-fulfiller', function(event) {
  let elem = $('.username-search');
  let term = $(this).data('username');
  let count = elem.length;
  let $search;

  elem.each((index, select) => {
    if (!select.value) {
      $search = $(select).data('select2').dropdown.$search || $(select).data('select2').selection.$search;
    } else if (index === count - 1) {
      add_row();
      let newSelect = $('.username-search:last');

      $search = newSelect.data('select2').dropdown.$search || newSelect.data('select2').selection.$search;
    }
  });
  $search.val(term);
  $search.trigger('input');

});
