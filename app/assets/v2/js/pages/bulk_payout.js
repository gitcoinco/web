const rateUser = (elem) => {
  let userSelected = $(elem).select2('data')[0].text;

  $(elem).parents('.new-user').find('[data-open-rating]').data('openUsername', userSelected.trim());
};

const normalizeUsername = function(username) {
  if (username.indexOf('@') != 0) {
    return '@' + username;
  }
  return username;
};

needWalletConnection();

window.addEventListener('dataWalletReady', function(e) {
  update_registry(selectedAccount);
}, false);

$(document).ready(function($) {

  $(document).on('blur', '#amount', function(event) {
    event.preventDefault();
    update_registry(selectedAccount);
  });

  $(document).on('input', '.input_amount', function(event) {
    event.preventDefault();
    const percentage = $(this).text();
    const is_error = !$.isNumeric(percentage) || percentage < 0;

    if (is_error) {
      $(this).addClass('error');
      $(this).parents('tr').find('.amount').text(0);
    } else {
      $(this).removeClass('error');
      const decimals = 3;
      const amount = round(get_amount(percentage), decimals);

      $(this).parents('tr').find('.amount').text(amount);
    }
    update_registry(selectedAccount);
  });


  $(document).on('input', '.amount', function(event) {

    event.preventDefault();
    const amount = $(this).text();
    const is_error = amount < 0;

    if (is_error) {
      $(this).addClass('error');
      $(this).parents('tr').find('.input_amount').text(0);
    } else {
      $(this).removeClass('error');
      const decimals = 1;
      const percentage = round(get_percentage(amount), decimals);

      $(this).parents('tr').find('.input_amount').text(percentage);
    }
    update_registry(selectedAccount);
  });

  $(document).on('click', '.remove', function(event) {
    event.preventDefault();
    $(this).parents('.new-user').next('tr').remove();
    $(this).parents('.new-user').remove();
    $(this).focus();
    update_registry(selectedAccount);
  });

  var sendTransaction = function(i) {

    var transaction = document.transactions[i];

    if (!transaction) {
      _alert('All transactions have been sent.  Your bounty is now paid out.', 'info');
      $('#success_container').css('display', 'block');
      $('.row.content').css('display', 'none');
      return;
    }

    $('.entry').removeClass('active');
    $('.entry_' + transaction['id']).addClass('active');

    // cancel bounty
    if (transaction['type'] == 'cancel') {
      var callback = function(txid, error) {
        indicateMetamaskPopup(true);
        if (error) {
          _alert({ message: error }, 'danger');
        } else {
          const url = 'https://' + etherscanDomain() + '/tx/' + txid;
          const msg = 'This tx has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

          // send msg to frontend
          _alert(msg, 'info');
          sendTransaction(i + 1);

          // tell frontend that this issue has a pending tx
          localStorage[$('#issueURL').text()] = JSON.stringify({
            timestamp: timestamp(),
            dataHash: null,
            issuer: selectedAccount,
            txid: txid
          });
        }
      };

      var bounty = new web3.eth.Contract(bounty_abi, bounty_address());

      indicateMetamaskPopup();

      bounty.methods.killBounty(
        $('#standard_bounties_id').val()
      ).send({
        from: selectedAccount
      }).then((result) => {
        callback(result);
      }).catch(err => {
        callback(undefined, err);
        console.log(err);
      });


    } else {
      const email = '';
      const github_url = $('#issueURL').text();
      const from_name = document.contxt['github_handle'];
      const username = transaction['data']['to'];
      const amountInEth = transaction['data']['amount'];
      const comments_priv = '';
      const comments_public = '';
      const from_email = '';
      const accept_tos = $('#terms').is(':checked');
      const tokenAddress = transaction['data']['token_address'];
      const expires = 9999999999;

      var success_callback = function(txid) {
        const url = 'https://' + etherscanDomain() + '/tx/' + txid;
        const msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

        _alert(msg, 'info', 1000);
        sendTransaction(i + 1); // text transaction
      };

      var failure_callback = function() {
        $.noop(); // do nothing
      };

      return sendTip(
        email,
        github_url,
        from_name,
        username,
        amountInEth,
        comments_public,
        comments_priv,
        from_email,
        accept_tos,
        tokenAddress,
        expires,
        success_callback,
        failure_callback,
        false
      );
    }
  };

  $('#acceptBounty').on('click', function(e) {
    e.preventDefault();
    getFulfillers();
    update_registry(selectedAccount);

    if (!provider) {
      onConnect();
      return false;
    }

    if (!$('#terms').is(':checked')) {
      _alert('Please accept the TOS.', 'danger');
      return;
    }
    if (typeof document.transactions == 'undefined' || !document.transactions.length) {
      _alert('You do not have any transactions to payout.  Please add payees to the form.', 'danger');
      return;
    }
    var usernames = $('.username-search');

    for (var i = 0; i < usernames.length; i++) {
      var username = usernames[i].textContent.trim();

      if (username === null || username === '' || username === '@') {
        _alert('Please provide a valid recipient Github username', 'danger');
        return;
      }
    }
    sendTransaction(0);
  });

  $('document').ready(function() {
    add_row();

    $('.add_another').on('click', function() {
      add_row();
    });

  });
});

const get_amount = percent => {
  const total_amount = $('#amount').text();

  return percent * 0.01 * total_amount;
};

const get_percentage = amount => {
  const total_amount = $('#amount').text();

  return (amount * 100) / total_amount;
};

var add_row = function() {
  const bountyId = $('#bountyId').val();
  const num_rows = $('#payout_table tbody').find('tr.new-user').length;
  const input_amount = num_rows <= 1 ? 100 : '';
  const denomination = $('#token_name').text();
  const amount = get_amount(input_amount);
  let username = '';
  const html = `
    <tr class="new-user">
      <td class="pl-0 pb-0">
        <div class="pl-0">
          <select onchange="update_registry()" class="username-search custom-select w-100 ml-auto mr-auto"></select>
        </div>
      </td>
      <td>
        <fieldset id="${num_rows}-${bountyId}" >
          <div class="rating pt-2" data-open-rating=${bountyId} data-open-username=${username}>
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
      <td class="pb-0">
        <div class="input_amount position-relative" contenteditable="true">${input_amount}</div>
        <span class="label font-weight-bold position-relative float-right">%</span>
      </td>
      <td class="pb-0">
        <div class="amount position-relative" contenteditable="true">${amount}</div>
        <span class="label font-weight-bold denomination position-relative float-right">${denomination}</span>
      </td>
      <td class="pb-0">
        <a class="remove position-relative" href=#>
          <i class="fas fa-times mt-2"></i>
        </a>
      </td>
    </tr>
  `;

  $('#payout_table tbody').append(html);
  userSearch('.username-search:last', true);
  $('body .username-search').each(function() {
    $(this).on('select2:select', event => {
      rateUser($(this));
    });
  });

  $(this).focus();
};

const get_total_cost = function() {
  const rows = $('#payout_table tbody tr.new-user');
  let total = 0;

  for (let i = 0; i < rows.length; i += 1) {
    const $rows = $(rows[i]);
    const amount = parseFloat($rows.find('.amount').text());
    const username = $rows.find('.username-search').text();
    const is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';

    const amount_in_percentage = $rows.find('.input_amount');
    const amount_in_qty = $rows.find('.amount');

    if (username == '' || username == '@') {
      amount_in_percentage.attr('contenteditable', false);
      amount_in_percentage.attr('title', 'Add Github user to edit this field');

      $('.rating input:radio').attr('disabled', true);
      $('.rating').attr('title', 'Add Github user to rate them');

      amount_in_qty.attr('contenteditable', false);
      amount_in_qty.attr('title', 'Add Github user to edit this field');
    } else {
      amount_in_percentage.attr('contenteditable', true);
      amount_in_percentage.attr('title', null);

      $('.rating input:radio').attr('disabled', false);
      $('.rating').attr('title', null);

      amount_in_qty.attr('contenteditable', true);
      amount_in_qty.attr('title', null);
    }

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
  const over = round((original_amount - get_total_cost()) * -1, 4);
  const addr = new truncate(coinbase).elem;
  const pay_with_bounty = $('input[name=pay_with]:checked').val() == 'bounty';
  const amount_from_bounty = $('#amount').text() > get_total_cost() ? get_total_cost() : $('#amount').text();

  let transactions = [];

  first_transaction = {
    'id': 0,
    'type': 'cancel',
    'reason': 'Bounty Funds refund to your wallet',
    'amount': '<i class="fas fa-plus font-smaller-7 pr-1 position-relative"></i>' + original_amount + ' ' + denomination
  };

  $('#summary_wallet_address').text(addr);
  $('#summary_wallet_amount').text(over);
  $('#summary_bounty_amount').text(amount_from_bounty);

  if (pay_with_bounty) {

    if (over > 0) {
      $('.overageAlert').css('display', 'inline-block');
      $('#total_overage').html(over + ' ' + denomination);
      $('#address_ending').html(addr + ' ');
      $('.summary_wallet_info').show();
    } else {
      $('.overageAlert').css('display', 'none');
      $('.summary_wallet_info').hide();
    }
    $('.summary_bounty_info').show();
    $('.tipAlert').css('display', 'none');
    transactions.push(first_transaction);

  } else {

    $('.summary_bounty_info').hide();
    $('.tipAlert').css('display', 'inline-block');
    $('#total_tip_overage').html(tc + ' ' + denomination);
    $('#address_tip_ending').html(addr + ' ');
    $('#preview_tip_overage').html(tc + ' ' + denomination);
    $('.overageAlert').css('display', 'none');
    $('.summary_wallet_info').show();
  }

  for (let j = 0; j <= num_rows; j++) {
    var $row = $('#payout_table tbody').find('tr:nth-child(' + (j + 1) + ')');
    const amount = parseFloat($row.find('.amount').text());
    const username = $row.find('.username-search').text();

    if (username == '')
      continue;

    transaction = {
      'id': j,
      'type': 'tip',
      'reason': 'Payout to ' + normalizeUsername(username),
      'amount': '<i class="fas fa-minus font-smaller-7 pr-1 position-relative"></i>' + amount + ' ' + denomination,
      'data': {
        'to': username,
        'amount': amount,
        'denomination': denomination,
        'token_address': $('#token_address').val()
      }
    };

    const is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';

    if (!is_error)
      transactions.push(transaction);
  }

  $('#transaction_registry tr.entry').remove();
  $('#metamask-txn-count').text(transactions.length);

  for (let k = 0; k < transactions.length; k += 1) {
    const trans = transactions[k];
    let direction;

    if (trans.type == 'cancel') {
      direction = '<span class="direction in font-caption font-weight-semibold ml-2 py-1 px-3">IN</span>';
    } else {
      direction = '<span class="direction out font-caption font-weight-semibold ml-2 py-1 px-3">OUT</span>';
    }

    const html = `<tr class='entry entry_${trans['id']}'>
      <td class="text-center">${k + 1}</td>
      <td class="font-weight-semibold">${trans['amount']} ${direction}</td>
      <td>${trans['reason']}</td>
    </tr>`;

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


$('input[type=radio][name=pay_with]').on('change', event => {
  update_registry(selectedAccount);
});
