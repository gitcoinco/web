(function($) {
  function round(amount, decimals) {
    return Math.round(((amount) * Math.pow(10, decimals))) / Math.pow(10, decimals);
  }

  var this_player = 'Player X';
  var gameboard = {
    "Player A": [1, 1, 4, 5],
    "Player X": [1, 1, 1, 1],
    "Player Y": [1, 1, 0, 0],
    "Player Z": [1, 1, 1, 1],
  }
  var allocation = 100;

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
    console.log(divisor);
    for (var key1 in matches) {
      matches[key1] *= divisor
    }
    return matches;
  }

  console.log(get_votes_by_player(gameboard))

  var render_gameboard = function(gameboard){
    let votes = get_votes_by_player(gameboard);
    let matches = get_matches_by_player(gameboard);
    let $target = $("#gameboard");

    // header
    $target.html('<table>');
    $target.append('<tr>');
    $target.append('<td>&nbsp;</td>');
    for (var key1 in gameboard) {
      $target.append(`<td>${key1}</td>`);
    }
    $target.append(`<td>Votes</td>`);
    $target.append(`<td>Match Amount</td>`);
    $target.append('</tr>');

    // gameboard
    for (var key1 in gameboard) {
      let entries = gameboard[key1];
      var subhtml = '';
      for (var key2 in entries) {
        let entry = entries[key2];
        let editable = key1 == this_player;
        let _class = editable ? '' : 'readonly';
        subhtml += `<td><input type=number ${_class} value=${entry}></td>`
      }
      let html = `
      <tr>
      <td>
      ${key1}
      </td> ${subhtml} 
      <td>
        ${votes[key1]} 
      </td>
      <td>
        ${round(matches[key1], 2)} 
      </td>
      <td>
        <span class=comment><span>
      </td>
      </tr>
            `;
      $target.append(html);
    }

    // footer
    $target.append('<tr><td>Sum</td><tr>');
    $target.append('<tr><td>Match Amount</td><tr>');

  }
  render_gameboard(gameboard);

})(jQuery);
