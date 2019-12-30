google.charts.load('current', { packages: [ 'corechart', 'bar' ]});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
  var target = document.getElementById('grant_chart');

  if (!target) {
    return;
  }
  var data = google.visualization.arrayToDataTable(document.history);

  var view = new google.visualization.DataView(data);
  var width = parseInt($('#grant_stats_graph').width());

  var ticks = [];
  var increment = 100;

  if (document.max_graph > 1000) {
    increment = 1000;
  }
  if (document.max_graph > 10000) {
    increment = 10000;
  }

  for (var i = 0; (i * increment) < document.max_graph; i += 1) {
    ticks.push(i * increment);
  }

  var options = {
    legend: { position: 'none' },
    bar: { groupWidth: '75%' },
    colors: [ '#011f4b', '#03396c', '#005b96', '#b3cde0' ],
    isStacked: true,
    backgroundColor: 'transparent',
    height: 400,
    width: width,
    vAxis: { title: 'USD', ticks: ticks, format: 'short', gridlines: { color: 'transparent' } }
  };

  var chart = new google.visualization.ColumnChart(target);

  chart.draw(view, options);
}

$(window).resize(function() {
  drawChart();

});
