(function($) {
  function round(amount, decimals) {
    return Math.round(((amount) * Math.pow(10, decimals))) / Math.pow(10, decimals);
  }

  var this_player = 'Player C';
  var players_to_seats = [
    "Player A",
    "Player B",
    "Player C",
    "Player D",
  ]
  var gameboard = [
    [1, 1, 4, 5],
    [1, 1, 1, 1],
    [1, 1, 0, 0],
    [1, 1, 1, 1],
  ];
  var allocation = 100;

  var get_my_seat = function(gameboard){
    for (var key1 in gameboard) {
      if(players_to_seats[key1] == this_player){
        return key1;
      }
    }
  }

  var get_total = function(gameboard){
    var total = 0;
    for (var key1 in gameboard) {
      for (var key2 in gameboard[key1]) {
        let amount = gameboard[key1][key2];
        total += parseFloat(amount);
      }
    }
    return total;
  }

  var flip_boardgame = function(gameboard){
    var new_boardgame = JSON.parse(JSON.stringify(gameboard));
    for (var i in gameboard) {
      for (var j in gameboard[i]) {
        new_boardgame[i][j] = gameboard[j][i]
      }
    }

    return new_boardgame;
  }

  var get_votes_by_player = function(gameboard){
    let total = get_total(gameboard);
    var votes = {};
    for (var key1 in gameboard) {
      var sumAmount = 0;
      for (var key2 in gameboard[key1]) {
        let amount = gameboard[key1][key2];
        sumAmount += (parseFloat(amount));
      }
      votes[key1] = sumAmount;
    }
    return votes;
  }

  var get_matches_by_player = function(gameboard){
    let total = get_total(gameboard);
    var runningSum = 0
    var matches = {};
    for (var key1 in gameboard) {
      let sumAmount = 0;
      for (var key2 in gameboard[key1]) {
        let amount = gameboard[key1][key2];
        sumAmount += Math.sqrt(parseFloat(amount));
      }
      matches[key1] = sumAmount;
      runningSum += sumAmount;
    }
    let divisor = total/runningSum;
    for (var key1 in matches) {
      matches[key1] *= divisor
    }
    return matches;
  }

  var render_gameboard = function(gameboard){
    let votes_given = get_votes_by_player(gameboard);
    let votes_received = get_votes_by_player(flip_boardgame(gameboard));
    let matches_given = get_matches_by_player(gameboard);
    let matches_received = get_matches_by_player(flip_boardgame(gameboard));
    let $target = $("#gameboard");

    // header
    $target.html('<table>');
    $target.append('<tr>');
    $target.append('<td>&nbsp;</td>');
    for (var key1 in gameboard) {
      $target.append(`<td>${players_to_seats[key1]}</td>`);
    }
    $target.append(`<td>Votes Given</td>`);
    $target.append(`<td>Match Amount Given</td>`);
    $target.append('</tr>');

    // gameboard
    for (var key1 in gameboard) {
      let entries = gameboard[key1];
      var subhtml = '';
      for (var key2 in entries) {
        let entry = entries[key2];
        let editable = players_to_seats[key1] == this_player;
        let _class = editable ? '' : 'readonly';
        subhtml += `<td><input type=number ${_class} min=0 max=${allocation} value=${entry}></td>`
      }
      let html = `
      <tr class=player_row>
      <td>
      ${players_to_seats[key1]}
      </td> ${subhtml} 
      <td>
        ${votes_given[key1]} 
      </td>
      <td>
        ${round(matches_given[key1], 2)} 
      </td>
      <td>
        <span class=comment><span>
      </td>
      </tr>
            `;
      $target.append(html);
    }

    // footer
    $target.append('<tr>');
    $target.append('<td>Votes Recevied</td>');
    for (var key1 in gameboard) {
      $target.append(`<td>${votes_received[key1]}</td>`);
    }
    $target.append('</tr><tr>');
    $target.append('<td>Match Amount Received</td>');
    for (var key1 in gameboard) {
      $target.append(`<td>${round(matches_received[key1],2)}</td>`);
    }
    $target.append('</tr>');

  }
  render_gameboard(gameboard);

  var get_gameboard = function(){
    var new_boardgame = JSON.parse(JSON.stringify(gameboard));
    let rows = $("#gameboard tr.player_row");
    for(var i=0; i<rows.length; i++){
      let row = rows[i];
      let targets = $(row).find('input');
      for(var j=0; j<targets.length; j++){
        let target=$(targets[j]).val();
        gameboard[i][j] = target
      }
    }
    return gameboard;
  }

  $(document).on('change', '#gameboard input', function(e) {
    // validating input
    let val = $(this).val();

    let new_gameboard = get_gameboard();
    var validation_passed = true;
    if(val < 0) validation_passed=false;
    let votes_given = get_votes_by_player(new_gameboard);
    let my_seat = get_my_seat(gameboard);
    let my_votes = votes_given[my_seat];
    if(my_votes > allocation) validation_passed=false;
    if(!validation_passed){
      $(this).val(0);
      return;
    }

    // validation passed; update board
    gameboard = new_gameboard
    render_gameboard(gameboard);
  });


})(jQuery);
