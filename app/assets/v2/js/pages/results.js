google.charts.load('current', { packages: [ 'corechart', 'bar' ]});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(repoChart);
google.charts.setOnLoadCallback(communityChart);
google.charts.setOnLoadCallback(jdiChart);

function drawChart() {
  var data = google.visualization.arrayToDataTable(document.bounty_history);

  var view = new google.visualization.DataView(data);

  var options = {
    legend: { position: 'none' },
    bar: { groupWidth: '50%' },
    colors: [ '#fbd0e6', '#FFCE08', '#25E899', '#3E00FF', '#F9006C' ],
    isStacked: true,
    backgroundColor: 'transparent',
    height: 400,
    vAxis: { title: 'USD', ticks: [ 0, document.max_bounty_history ], format: 'short', gridlines: { color: 'transparent' } }
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('bounty_universe_chart'));

  chart.draw(view, options);
}

function repoChart() {
  var data = google.visualization.arrayToDataTable(document.platform_stats);

  var options = {
    pieHole: 0.8,
    pieSliceText: 'none',
    legend: 'none',
    height: 300,
    width: 300,
    colors: [ '#3E00FF', '#25E899', '#FFCE08' ]
  };

  var chart = new google.visualization.PieChart(document.getElementById('repo_chart'));

  chart.draw(data, options);
}

function communityChart() {
  var data = google.visualization.arrayToDataTable(document.members_history);

  var options = {
    curveType: 'function',
    legend: { position: 'none' },
    backgroundColor: 'transparent',
    height: 400,
    vAxis: { ticks: document.slack_ticks, gridlines: { color: 'transparent' } },
    hAxis: { ticks: [ 'LAUNCH', 'TODAY' ], scaleType: 'log' },
    series: { 0: { color: '#F9006C' } }
  };

  var chart = new google.visualization.LineChart(document.getElementById('community_chart'));

  chart.draw(data, options);
}

// TODO: DRY
function jdiChart() {
  var data = google.visualization.arrayToDataTable(document.jdi_history);

  var options = {
    curveType: 'function',
    legend: { position: 'none' },
    backgroundColor: 'transparent',
    height: 400,
    vAxis: { ticks: document.jdi_ticks, gridlines: { color: 'transparent' } },
    hAxis: { ticks: [ 'LAUNCH', 'TODAY' ], scaleType: 'log' },
    series: { 0: { color: '#15003E' } }
  };

  var chart = new google.visualization.LineChart(document.getElementById('jdi_chart'));

  chart.draw(data, options);
}

$(window).resize(function() {
  jdiChart();
  drawChart();
  repoChart();
  communityChart();
});
