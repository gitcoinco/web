google.charts.load('current', { packages: [ 'corechart', 'bar' ]});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(repoChart);
google.charts.setOnLoadCallback(communityChart);
google.charts.setOnLoadCallback(jdiChart);

function drawChart() {
  var data = google.visualization.arrayToDataTable(document.bounty_history);

  var view = new google.visualization.DataView(data);
  var width = parseInt(window.innerWidth * .92);

  if (width > document.body.clientWidth) {
    width = document.body.clientWidth - 50;
  }
  var options = {
    legend: { position: 'none' },
    bar: { groupWidth: '45%' },
    colors: [ '#011f4b', '#03396c', '#005b96', '#6497b1', '#b3cde0', '#d3ddf0', '#DDDDDD' ],
    isStacked: true,
    backgroundColor: 'transparent',
    height: 400,
    width: width,
    vAxis: { title: 'USD', ticks: [ 0, 10000, 100000, 200000, 300000, 400000, 500000, 600000, document.max_bounty_history ], format: 'short', gridlines: { color: 'transparent' } }
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('bounty_universe_chart'));

  chart.draw(view, options);
}

function repoChart() {
  var pie_charts = [
    [ 'repo_chart', document.platform_stats ],
    [ 'breakeven_chart', document.breakeven_stats ]
  ];

  for (var i = 0; i < pie_charts.length; i += 1) {
    var stats = pie_charts[i][1];
    var id = pie_charts[i][0];
    var data = google.visualization.arrayToDataTable(stats);

    var options = {
      pieHole: 0.8,
      pieSliceText: 'none',
      legend: 'none',
      height: 300,
      width: 300,
      colors: [ '#011f4b', '#03396c', '#005b96' ]
    };

    var chart = new google.visualization.PieChart(document.getElementById(id));

    chart.draw(data, options);
  }

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

console.log('here');

$(document).ready(function() {
  setInterval(function() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > 500 && !document.offset_loaded) {
      $('img').unveil(200);
      document.offset_loaded = true;
    }
  }, 3000);
  $.get('/activity', function(html) {
    $('#activities').html($(html).find('.activity_stream').html());
  });
  $('.view_more').click(function(e) {
    e.preventDefault();
    $('.hackathon-breakdown .hidden').removeClass('hidden');
    $(this).remove();
  });
  $('#leaderboard_nav .nav-link').click(function(e) {
    let id = $(this).attr('href');
    let target = $(this).data('target');
    let target_search = $(this).data('targetsearch');

    e.preventDefault();
    $('.leaderboard_target').addClass('hidden');
    $('.nav-link').removeClass('active');
    $('.always_show').removeClass('hidden');
    $(id).removeClass('hidden');
    $(this).addClass('active');
    if (target) {
      $(id).html('Loading...');
      $.get(target, function(html) {
        html = html.replace(/data-src/g, 'src');
        $(id).html($(html).find(target_search));
        $(id).find('.img-fluid').remove();
      });
    }
  });
  $('#leaderboard_nav .nav-link:first-child').click();
});
