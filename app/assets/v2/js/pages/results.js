google.charts.load('current', { packages: [ 'corechart', 'bar' ]});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(repoChart);
google.charts.setOnLoadCallback(communityChart);
google.charts.setOnLoadCallback(jdiChart);

function drawChart() {
  var data = google.visualization.arrayToDataTable(document.bounty_history);

  var view = new google.visualization.DataView(data);
  var width = 800;

  if (width > document.body.clientWidth) {
    width = document.body.clientWidth - 50;
  }
  var options = {
    legend: { position: 'none' },
    bar: { groupWidth: '50%' },
    colors: [ '#011f4b', '#03396c', '#005b96', '#6497b1', '#b3cde0', '#d3ddf0', '#DDDDDD' ],
    isStacked: true,
    backgroundColor: 'transparent',
    height: 400,
    width: width,
    vAxis: { title: 'USD', ticks: [ 0, 10000, 50000, 100000, 150000, 200000, document.max_bounty_history ], format: 'short', gridlines: { color: 'transparent' } }
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
    colors: [ '#011f4b', '#03396c', '#005b96' ]
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
