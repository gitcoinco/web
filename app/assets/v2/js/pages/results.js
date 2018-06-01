google.charts.load('current', { packages: [ 'corechart', 'bar' ]});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(repoChart);
google.charts.setOnLoadCallback(communityChart);

// TODO: Implement Real Data for Graphs

function drawChart() {
  var data = google.visualization.arrayToDataTable([
    [ '', 'Open / Available', { role: 'annotation' }, 'Claimed / In Progress', { role: 'annotation' }, 'Completed', { role: 'annotation' }, 'CodeFund Bounties' ],
    [ 'Q1 2017', 20000, '20K', 40000, '40K', 50000, '50K', 5000 ],
    [ 'Q2 2017', 24000, '24K', 50000, '50K', 50000, '50K', 5000 ],
    [ 'Q3 2017', 30000, '30K', 60000, '60K', 50000, '50K', 5000 ],
    [ 'Q4 2017', 40000, '40K', 70000, '70K', 50000, '50K', 5000 ],
    [ 'Q1 2018', 50000, '50K', 80000, '80K', 50000, '50K', 5000 ]
  ]);

  var view = new google.visualization.DataView(data);

  var options = {
    legend: { position: 'none' },
    bar: { groupWidth: '50%' },
    colors: [ '#FFCE08', '#25E899', '#3E00FF', '#F9006C' ],
    isStacked: true,
    backgroundColor: 'transparent',
    height: 400,
    vAxis: { title: 'USD', ticks: [ 0, 150000 ], format: 'short', gridlines: { color: 'transparent' } }
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('bounty_universe_chart'));

  chart.draw(view, options);
}

function repoChart() {
  var data = google.visualization.arrayToDataTable([
    [ 'Repo', 'Bounties' ],
    [ 'Open & Claimed Bounties', 200 ],
    [ 'Claimed Bounties in Progress', 150 ],
    [ 'More than 3 bounties in Progress', 105 ]
  ]);

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
  var data = google.visualization.arrayToDataTable([
    [ 'Year', 'Members' ],
    [ 'Launch', 0 ],
    [ '', 100 ],
    [ '', 500 ],
    [ '', 1000 ],
    [ 'Today', 2000 ]
  ]);

  var options = {
    curveType: 'function',
    legend: { position: 'none' },
    backgroundColor: 'transparent',
    height: 400,
    vAxis: { ticks: [ 0, 500, 1000 ], gridlines: { color: 'transparent' } },
    hAxis: { ticks: [ 'LAUNCH', 'TODAY' ], scaleType: 'log' },
    series: { 0: { color: '#F9006C' } }
  };

  var chart = new google.visualization.LineChart(document.getElementById('community_chart'));

  chart.draw(data, options);
}

$(window).resize(function() {
  drawChart();
  repoChart();
  communityChart();
});