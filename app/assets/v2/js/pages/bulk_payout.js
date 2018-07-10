$(document).ready(function ($) {
  var random_id = function () {
    var id_num = Math.random().toString(9).substr(2, 3);
    var id_str = Math.random().toString(36).substr(2);
    return id_num + id_str;
  }

  var make_table = function(){
    var tbl = '';
    tbl += '<table class="table table-hover" id ="payout_table">'
    tbl += '<thead>';
    tbl += '<tr>';
    tbl += '<th>Percent(%)</th>';
    tbl += '<th>Amount</th>';
    tbl += '<th>Github Username</th>';
    tbl += '<th>Options</th>';
    tbl += '</tr>';
    tbl += '</thead>';
    tbl += '<tbody>';
    $(document).find('.tbl_user_data').html(tbl);
  }

  //--->make div editable > start
  $(document).on('click', '.row_data', function (event) {
    event.preventDefault();

    if ($(this).attr('edit_type') == 'button') {
        return false;
    }

    //make div editable
    $(this).closest('div').attr('contenteditable', 'true');
    //add bg css
    $(this).addClass('bg-warning').css('padding', '5px');

    $(this).focus();
  })
  //--->make div editable > end


  //--->save single field data > start
  $(document).on('focusout', '.row_data', function (event) {
    event.preventDefault();
    if ($(this).attr('edit_type') == 'button') {
        return false;
    }

    var row_id = $(this).closest('tr').attr('row_id');

    var row_div = $(this)
    .removeAttr('contenteditable') //make div editable
    .removeClass('bg-warning') //add bg css
    .css('padding', '')

    var col_name = row_div.attr('col_name');
    var col_val = row_div.html();


    if (col_name == 'fname') {
        var pos1 = col_val.indexOf("%");
        if (pos1 != -1) {
            var resp = col_val.substr(0, pos1);
        }
        procenat = Number(resp);
    }
    alert('percent' + procenat.toString());
    var arr = {};
    arr[col_name] = col_val;

    //use the "arr" object for your ajax call
    $.extend(arr, { row_id: row_id });

    //out put to show
    $('.post_msg').html('<pre class="bg-success">' + JSON.stringify(arr, null, 2) + '</pre>');

  })
  var add_row = function () {
    var amount = 1;
    var denomination = 'ETH';
    var html = '<tr><td><div id="procent1" contenteditable="true">0</div></td><td><div contenteditable="true">'+amount+' '+denomination+'</div></td><td><div contenteditable="true">@</div></td><td><a class=remove href=#>X</a></td></tr>'
    $('#payout_table').append(html);
    $(this).focus();
  };

  $('document').ready(function () {
      make_table();
      $('.add_another').click(add_row);
      add_row();
  });
});