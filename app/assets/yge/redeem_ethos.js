/* eslint-disable no-console */
window.onload = function() {
  waitforWeb3(function() {
    $('forwarding_address').value = web3.eth.accounts[0];
    $('forwarding_address').disabled = true;
  });

  setTimeout(function() {
    $('loading').style.display = 'none';
    $('send_eth').style.display = 'block';
  }, 500);

  /* var dataset = {
    nodes: [
      {
        'name': 'owocki',
        'img': window.location.origin + '/ethos/proxy/?image=' + encodeURIComponent('https://twitter.com/owocki/profile_image?size=original')
      },
      {
        'name': 'mbeacom',
        'img': window.location.origin + '/ethos/proxy/?image=' + encodeURIComponent('https://twitter.com/mbeacom/profile_image?size=original')
      },
      {
        'name': 'eswara_sai',
        'img': window.location.origin + '/ethos/proxy/?image=' + encodeURIComponent('https://twitter.com/eswara_sai/profile_image?size=original')
      },
      {
        'name': 'thelostone-mc',
        'img': window.location.origin + '/ethos/proxy/?image=' + encodeURIComponent('https://gitcoin.co/static/avatar/thelostone-mc/')
      }
    ],
    edges: [
      {source: 0, target: 1, distance: 200},
      {source: 1, target: 2, distance: 50},
      {source: 2, target: 3, distance: 100}
    ]
  };

  generateGraph(dataset); */
};

function redeemCoin() {
  mixpanel.track('Redeem EthOS Coin Click', {});
  metaMaskWarning();

  var forwarding_address = $('forwarding_address').value;
  var twitter_username = $('twitter_username').value;

  // Check for valid address
  isValidForwardingAddress = forwarding_address.indexOf('0x') != -1;
  if (!forwarding_address || !isValidForwardingAddress) {
    _alert({message: gettext('Not a valid forwarding address')}, 'error');
    return;
  }

  // Check for twitter username
  if (!twitter_username) {
    _alert({message: gettext('Please enter your Twitter username')}, 'error');
    return;
  }

  twitter_username = twitter_username.trim();

  var sendEthInnerHTML = $('send_eth').innerHTML;

  $('send_eth').innerHTML = '<img src="/static/yge/images/loading_v2.gif" style="max-width: 70px; max-height: 70px;"><br><h4>Submitting to the blockchain...</h4>';

  fetch(window.location.href, {
    method: 'POST',
    body: JSON.stringify({
      address: forwarding_address.trim(),
      username: twitter_username
    })
  })
    .then(
      function(response) {
        response.json().then(function(data) {
          if (data.status === 'OK') {
            generateGraph(data.dataset, twitter_username, data.message);
          } else {
            if (data.message.indexOf('Address has an invalid EIP checksum') !== -1) {
              _alert({message: 'Please enter a valid checksum address.'}, 'warning');
            } else {
              _alert({message: data.message}, 'error');
            }

            $('send_eth').innerHTML = sendEthInnerHTML;

            // Prefill the input fields as the form is attached dynamically to the DOM
            setTimeout(function() {
              document.getElementById('send_eth').querySelector('#forwarding_address').value = forwarding_address;
              document.getElementById('send_eth').querySelector('#twitter_username').value = twitter_username;
            }, 100);

            mixpanel.track('Redeem EthOS Coin Error', {
              error: data.message
            });
          }
        });
      }
    )
    .catch(function(err) {
      console.log('Fetch Error :-S', err);
    });
}

var generateGraph = function(dataset, username, txid) {
  var w = 600;
  var h = 400;

  var force = d3.layout.force()
    .nodes(dataset.nodes)
    .links(dataset.edges)
    .size([ w, h ])
    .linkDistance(function(link) {
      return link.distance;
    })
    .charge([-150])
    .start();

  var colors = d3.scale.category10();

  var svg = d3.select('#graph')
    .append('svg')
    .attr('width', w)
    .attr('height', h);

  var edges = svg.selectAll('line')
    .data(dataset.edges)
    .enter()
    .append('line')
    .attr('marker-end', 'url(#arrowhead)')
    .style('stroke', '#CACACA')
    .style('stroke-width', 2);

  var nodes = svg.selectAll('circle')
    .data(dataset.nodes)
    .enter()
    .append('circle')
    .attr('r', 16)
    .attr('stroke', '#1AB56D')
    .attr('stroke-width', '0.2%')
    .attr('fill', function(d) {
      return 'url(#' + d.name + ')';
    });

  var label = svg.selectAll('.mytext')
    .data(dataset.nodes)
    .enter()
    .append('text')
    .text(function(d) {
      return d.name;
    })
    .attr('dx', 14)
    .attr('dy', '1.2em')
    .style('fill', '#555');

  svg.append('defs').append('marker')
    .attr({
      'id': 'arrowhead',
      'viewBox': '-0 -5 20 10',
      'refX': 23,
      'refY': 0,
      'orient': 'auto',
      'markerWidth': 10,
      'markerHeight': 10,
      'xoverflow': 'visible'
    })
    .append('svg:path')
    .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
    .attr('fill', '#CACACA')
    .attr('stroke', '#CACACA');


  svg.selectAll('pattern').data(dataset.nodes).enter().append('pattern')
    .attr('id', function(d) {
      return d.name;
    })
    .attr('x', '0%')
    .attr('y', '0%')
    .attr('height', '100%')
    .attr('width', '100%')
    .attr('viewBox', '0 0 512 512')
    .append('image')
    .attr('x', '0%')
    .attr('y', '0%')
    .attr('height', '512')
    .attr('width', '512')
    .attr('xlink:href', function(d) {
      return d.img;
    });

  force.on('tick', function() {
    edges.attr('x1', function(d) {
      return d.source.x;
    })
      .attr('y1', function(d) {
        return d.source.y;
      })
      .attr('x2', function(d) {
        return d.target.x;
      })
      .attr('y2', function(d) {
        return d.target.y;
      });
    nodes.attr('cx', function(d) {
      return d.x;
    })
      .attr('cy', function(d) {
        return d.y;
      });
    label.attr('x', function(d) {
      return d.x;
    })
      .attr('y', function(d) {
        return d.y - 10;
      });
  });

  setTimeout(function() {
    svgAsPngUri(svg.node(), {}, function(uri) {
      fetch('/ethos/tweet/', {
        method: 'POST',
        body: JSON.stringify({
          media: uri.replace(/^data:image\/(png|jpg);base64,/, ''),
          username: username
        })
      })
        .then(
          function(response) {
            response.json().then(function(data) {
              mixpanel.track('Redeem EthOS Coin Success', {});
              startConfetti();

              // TODO: Display the stats page after posting the tweet
              $('send_eth').innerHTML = '<h1>Success 🚀!</h1> <a href="https://' + etherscanDomain() + '/tx/' + txid + '" target="_blank" rel="noopener noreferrer">See your transaction on the blockchain here</a>.<br><br><span id="mighttake">It might take a few minutes to sync, depending upon: <br> - network congestion<br> - network fees that sender allocated to transaction<br></span><br><a href="/" class="button" style="background-color: #15003e;">⬅ Check out Gitcoin.co</a>';
            });
          }
        )
        .catch(function(err) {
          console.log('Tweet Error', err);
          mixpanel.track('Redeem EthOS Coin Error', {});
        });
    });
  }, 5000);
};
