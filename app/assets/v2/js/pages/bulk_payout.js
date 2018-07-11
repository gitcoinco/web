var round = function(num, decimals){
    return Math.round(num * 10**decimals) / 10**decimals;  
}

$(document).ready(function($) {
  var random_id = function() {
    var id_num = Math.random().toString(9).substr(2, 3);
    var id_str = Math.random().toString(36).substr(2);

    return id_num + id_str;
  };

  var make_table = function() {
    var tbl = '';

    tbl += '<table class="table table-hover" id ="payout_table">';
    tbl += '<thead>';
    tbl += '<tr>';
    tbl += '<th>Github Username</th>';
    tbl += '<th>Percent(%)</th>';
    tbl += '<th>Amount</th>';
    tbl += '<th></th>';
    tbl += '</tr>';
    tbl += '</thead>';
    tbl += '<tbody>';
    $(document).find('.tbl_user_data').html(tbl);
  };

  $(document).on('blur', '#amount', function(event) {
    event.preventDefault();
    update_registry();
  });


  $(document).on('input', '.percent', function(event) {
    event.preventDefault();
    var percent = $(this).text();
    var is_error = !$.isNumeric(percent) || percent < 0;
    if(is_error){
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
    if(username == '' || username == '@'){
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


  var get_amount = function(percent){
    var total_amount = $("#amount").val();
    return percent * 0.01 * total_amount;
  };

  var add_row = function() {
    var num_rows = $("#payout_table").find('tr').length;
    var percent = num_rows <= 1 ? 100 : 0;
    var denomination = $("#token_name").text();
    var amount = get_amount(percent);
    var html = '<tr><td><div class=username contenteditable="true">@</div></td><td><div class="percent" contenteditable="true">'+percent+'</div></td><td><div><span class=amount>' + amount + '</span> <span class=denomination>' + denomination + '</span></div></td><td><a class=remove href=#>X</a></td></tr>';
    $('#payout_table').append(html);
    $(this).focus();
  };

  var get_total_cost = function() {
    var num_rows = $("#payout_table").find('tr').length;
    var total = 0;
    for(var i = 1; i<num_rows; i+=1){
      var $row = $("#payout_table").find('tr:nth-child('+i+')');
      var amount = parseFloat($row.find('.amount').text());
      var username = $row.find('.username').text();
      var is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';
      if(!is_error){
        total += amount;
      }
    }
    return total;
  };

  var update_registry = function() {
    var num_rows = $("#payout_table").find('tr').length;
    var tc = round(get_total_cost(), 2);
    var denomination = $("#token_name").text();
    var original_amount = $("#original_amount").val();
    var net = round(original_amount - tc, 2);
    $("#total_cost").html(tc + " " + denomination)
    $("#total_net").html(net + " " + denomination)

    var transactions = [];
    first_transaction = {
      'id': 1,
      'reason': 'Refund of Bounty Stake',
      'amount': '+' + original_amount + " " + denomination,
    }
    transactions.push(first_transaction);
    for(var i = 1; i<num_rows; i+=1){
      var $row = $("#payout_table").find('tr:nth-child('+i+')');
      var amount = parseFloat($row.find('.amount').text());
      var username = $row.find('.username').text();
      transaction = {
        'id': i + 1,
        'reason': 'Payment to ' + username,
        'amount': "-" + amount + " " + denomination,
      }
      var is_error = !$.isNumeric(amount) || amount <= 0 || username == '' || username == '@';
      if(!is_error)
        transactions.push(transaction);
    }
    //paint on screen
    $("#transaction_registry tr.entry").remove();
    for(var i = 0; i<transactions.length; i+=1){
      var trans = transactions[i];
      var html = "<tr class='entry entry_"+trans['id']+"'><td>"+trans['id']+"</td><td>"+trans['amount']+"</td><td>"+trans['reason']+"</td></tr>"
      $("#transaction_registry").append(html);
    }

    document.transactions_preview = transactions;
  };

  $('document').ready(function() {
    make_table();
    add_row();
    update_registry();

    $('.add_another').click(add_row);

  });
});