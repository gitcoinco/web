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
    vAxis: { title: 'USD', ticks: [ 0, 1000000, 2 * 1000000, 3 * 1000000, 4 * 1000000, 5 * 1000000, 6 * 1000000, document.max_bounty_history ], format: 'short', gridlines: { color: 'transparent' } }
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

  if (!google || !google.visualization)
    return;

  const data = google.visualization.arrayToDataTable(document.jdi_history);

  const options = {
    curveType: 'function',
    legend: { position: 'none' },
    backgroundColor: 'transparent',
    height: 400,
    vAxis: { ticks: document.jdi_ticks, gridlines: { color: 'transparent' } },
    hAxis: { ticks: [ 'LAUNCH', 'TODAY' ], scaleType: 'log' },
    series: { 0: { color: '#15003E' } }
  };

  const chart = new google.visualization.LineChart(document.getElementById('jdi_chart'));

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
      $(id).html('<img style="margin: 20px 100px; height: 200px; width: 200px;" src=/static/v2/images/loading_v2.gif>');
      $.get(target, function(html) {
        html = html.replace(/data-src/g, 'src');
        $(id).html($(html).find(target_search));
        if (target.indexOf('countries') != -1) {
          $(id).find('.img-fluid').remove();
        }
      });
    }
  });
  setTimeout(function() {
    $('#leaderboard_nav .nav-link:first-child').click();

    $('#tweets').html(`
        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">And to <a href="https://twitter.com/owocki?ref_src=twsrc%5Etfw">@owocki</a> and the entire team at <a href="https://twitter.com/gitcoin?ref_src=twsrc%5Etfw">@gitcoin</a> <br><br>Thank you for making it so easy this time! You&#39;re everything that&#39;s good in this world 🌐😍 <a href="https://t.co/bVNIvUem01">pic.twitter.com/bVNIvUem01</a></p>&mdash; Mariano Conti | conti.eth (@nanexcool) <a href="https://twitter.com/nanexcool/status/1275513916714618882?ref_src=twsrc%5Etfw">June 23, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

          </div>
        </div>
        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">I&#39;m genuinely amazed by the projects in the <a href="https://twitter.com/ArweaveTeam?ref_src=twsrc%5Etfw">@ArweaveTeam</a> <a href="https://twitter.com/gitcoin?ref_src=twsrc%5Etfw">@gitcoin</a> incubator, these are incredible. Wow.</p>&mdash; Lasse Clausen (@lalleclausen) <a href="https://twitter.com/lalleclausen/status/1294320204470722560?ref_src=twsrc%5Etfw">August 14, 2020</a></blockquote> 
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">already 5 devs working on <a href="https://twitter.com/DemocracyEarth?ref_src=twsrc%5Etfw">@DemocracyEarth</a>&#39;s bounty on <a href="https://twitter.com/gitcoin?ref_src=twsrc%5Etfw">@gitcoin</a>.. and i&#39;m having some of the most interesting conversations about the task.<br><br>i&#39;m loving the bounty model <a href="https://twitter.com/owocki?ref_src=twsrc%5Etfw">@owocki</a>.<a href="https://t.co/pfJmqy9sJ1">https://t.co/pfJmqy9sJ1</a></p>&mdash; santi.eth 🐋👽 (@santisiri) <a href="https://twitter.com/santisiri/status/1268974194584440834?ref_src=twsrc%5Etfw">June 5, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">The idea of contributing to open source as a career instead of just being a hobby has never seemed more possible of a reality to me than it does through Gitcoin.<br><br>My referal link: <a href="https://t.co/RAlDj4LpEW">https://t.co/RAlDj4LpEW</a><br><br>I suggest looking at the quests firsts and hanging out in the Townsquare.</p>&mdash; Walid Mujahid وليد مجاهد (@walidmujahid1) <a href="https://twitter.com/walidmujahid1/status/1235288950119559171?ref_src=twsrc%5Etfw">March 4, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">And before I forget: Thanks to <a href="https://twitter.com/owocki?ref_src=twsrc%5Etfw">@owocki</a> and team for building the 💪💪 <a href="https://twitter.com/gitcoin?ref_src=twsrc%5Etfw">@gitcoin</a> platform! You&#39;re making the world a better place 🙏😎</p>&mdash; Michael Bauer 🔆 triplespeeder.eth (@TripleSpeeder) <a href="https://twitter.com/TripleSpeeder/status/1223728317242781697?ref_src=twsrc%5Etfw">February 1, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">Congrats to the entire <a href="https://twitter.com/gitcoin?ref_src=twsrc%5Etfw">@gitcoin</a> team on an amazing round 4 of CLR matching!<br><br>$144,810 given directly to open source initiatives that will benefit <a href="https://twitter.com/hashtag/Ethereum?src=hash&amp;ref_src=twsrc%5Etfw">#Ethereum</a> and grow our ecosystem.<br><br>Let&#39;s make round 5 even better 🚀<br><br>Oh and thanks to all the haters for the free marketing 😘 <a href="https://t.co/ljRt2Q9MOp">https://t.co/ljRt2Q9MOp</a></p>&mdash; Anthony Sassano | sassal.eth 👨‍🌾 (@sassal0x) <a href="https://twitter.com/sassal0x/status/1219791111901679618?ref_src=twsrc%5Etfw">January 22, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">Gitcoin Grants might be the most underrated experiment in Web3. <a href="https://t.co/uCeT4KHyPp">https://t.co/uCeT4KHyPp</a></p>&mdash; Spencer Noon (@spencernoon) <a href="https://twitter.com/spencernoon/status/1214392894246850560?ref_src=twsrc%5Etfw">January 7, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
          <blockquote class="twitter-tweet"><p lang="en" dir="ltr">One of the best way to start out in DeFi is working on a <a href="https://twitter.com/gitcoin?ref_src=twsrc%5Etfw">@gitcoin</a> bounty. Grab one of the many 4-digit prizes offered during the NYBW virtual hackathon:<a href="https://t.co/u9tTM4A7M6">https://t.co/u9tTM4A7M6</a></p>&mdash; Paul Razvan Berg (@PaulRBerg) <a href="https://twitter.com/PaulRBerg/status/1260622852161703938?ref_src=twsrc%5Etfw">May 13, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">Sooo happy with <a href="https://twitter.com/GetGitcoin?ref_src=twsrc%5Etfw">@GetGitcoin</a> results! Submitted an issue last night and by the morning I had a PR with exactly what I wanted!<a href="https://t.co/x0caRHusXV">https://t.co/x0caRHusXV</a> <a href="https://t.co/nBvsVvkz3q">pic.twitter.com/nBvsVvkz3q</a></p>&mdash; ⚡KAMESCG.ΞTH 🐺 (@KamesCG) <a href="https://twitter.com/KamesCG/status/981514994029297664?ref_src=twsrc%5Etfw">April 4, 2018</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>

        <div class="row py-1">
          <div class="col-12 offset-md-0 d-flex justify-content-center align-items-center ">
            <blockquote class="twitter-tweet"><p lang="en" dir="ltr">Gitcoin grants quadratic funding is not just for funds allocation, it&#39;s also a great signaling tool!<br><br>For the last few rounds, going to <a href="https://t.co/F4VFg2s7LJ">https://t.co/F4VFg2s7LJ</a> (sort by top match) has led me to discover a lot of really cool Ethereum projects I previously did not know about.</p>&mdash; vitalik.eth (@VitalikButerin) <a href="https://twitter.com/VitalikButerin/status/1243284318987878401?ref_src=twsrc%5Etfw">March 26, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
          </div>
        </div>
      `);

  }, 5000);
});
