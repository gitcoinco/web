$(document).ready(function() {
  $('#profile-tabs button').on('click', function() {
    document.location = $(this).attr('href');
  });

  if ($('.load-more').length) {
    $(window).scroll(function() {
      if ($('.load-more').isInViewport()) {
        $('.load-more').click();
      }
    });
  }
  $('#kudos-section').on('click', '.fa-sync', function(e) {
    e.preventDefault();
    e.stopPropagation();
    if ($(this).data('owned') == 'False') {
      _alert('To re-issue this kudos, please contact the sender and have them re-send it.', 'danger');
      return;
    }
    let url = '/kudos/sync/?pk=' + $(this).data('id');
    let $target = $(this).parents('.flip-card__extra-data').find('.block_explorer_link');

    $.get(url, function(response) {
      let block_ex_url = response['url'];
      let txid = response['txid'];

      $target.attr('href', block_ex_url);
      let txid_trunc = txid.substring(0, 5) + '...' + txid.substring(txid.length - 10, txid.length);

      $target.text(txid_trunc);
      $target.css('color', 'grey');
      setTimeout(function() {
        $target.css('color', 'white');
      }, 1000);
      _alert('Sync re-submitted to chain.', 'info', 1000);
    });
    $(this).remove();

  });


  $('#kudos-section').on('click keypress', '.flip-card', e => {
    if ($(e.target).is('a')) {
      e.stopPropagation();
      return;
    }
    $(e.currentTarget).toggleClass('turn');
  });
  $('#heatmap_parent').animate({ scrollLeft: '+=1000px' }, 'fast');
  setupTabs('#activity-tabs');

  const tabSection = document.querySelector('#activity-tabs-sections');
  const updateViewBtn = document.querySelector('#update-view-btn');

  let fetchInProgress = false;

  // update activity views when scroll happens
  function updateView(ignoreScrollOffset) {
    window.setTimeout(updateView, 300);

    if (fetchInProgress) {
      return;
    }

    const is_on_activity_tab = $('.profile-bounties--activities').length > 0;
    const are_there_no_tabs = $('#tab_controller .nav-link.active').length == 0;

    if (!is_on_activity_tab && !are_there_no_tabs) {
      return;
    }

    const activityContainer = document.querySelector('.tab-section.active .activities');
    const activityCount = activityContainer ? parseInt(activityContainer.getAttribute('count')) || 0 : 0;
    const loadingImg = document.querySelector('.loading_img');

    if (activityContainer && activityContainer.children.length < activityCount) {
      updateViewBtn.style['visibility'] = 'visible';
    } else {
      updateViewBtn.style['visibility'] = 'hidden';
      return;
    }

    if (activityContainer && (ignoreScrollOffset || window.scrollY >= tabSection.scrollHeight)) {
      const activityName = activityContainer.id;
      let page = parseInt(activityContainer.getAttribute('page')) || 0;

      fetchInProgress = true;
      loadingImg.className = loadingImg.className.replace('hidden', 'visible');

      const fetch_url = location.href.replace(location.hash, '').replace('?', '').replace('#', '');

      fetch(fetch_url + '?p=' + (++page) + '&a=' + activityName).then(
        function(response) {
          if (response.status === 200 || response.status === 204) {
            response.text().then(
              function(html) {
                const results = document.createElement('div');

                activityContainer.setAttribute('page', page);
                results.insertAdjacentHTML('afterBegin', html);

                const childs = results.children;

                while (childs.length) {
                  activityContainer.append(childs[0]);
                }

                fetchInProgress = false;
                loadingImg.className = loadingImg.className.replace('visible', 'hidden');
              }
            );
            return;
          }
          fetchInProgress = false;
          hideBusyOverlay();
        }
      ).catch(
        function() {
          fetchInProgress = false;
          loadingImg.className = loadingImg.className.replace('visible', 'hidden');
        }
      );
    }
  }

  if (updateViewBtn) {
    updateViewBtn.addEventListener('click',
      function() {
        updateView(true);
      },
      false
    );

    updateView();
  }
});

(function($) {

  $('.tooltip').bootstrapTooltip();

  // rep graph
  if ($('#earn_dataviz').length) {
    // Set the dimensions of the canvas / graph
    const margin = {top: 30, right: 30, bottom: 30, left: 70};
    const width = $('.container.position-relative').width() - margin.left - margin.right;
    const height = 120 - margin.top - margin.bottom;

    // Parse the date / time
    const parseDate = d3.time.format('%d-%b-%y').parse;

    // Set the ranges
    const x = d3.time.scale().range([ 0, width ]);
    const y = d3.scale.linear().range([ height, 0 ]);

    // Define the axes
    var xAxis = d3.svg.axis().scale(x)
      .orient('bottom').ticks(5);

    var yAxis = d3.svg.axis().scale(y)
      .orient('left').ticks(3);

    // Define the line
    var valueline = d3.svg.line()
      .x(function(d) {
        return x(d.date);
      })
      .y(function(d) {
        return y(d.close);
      });

    // Adds the svg canvas
    var svg = d3.select('#earn_dataviz')
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform',
        'translate(' + margin.left + ',' + margin.top + ')');

    // Get the data
    d3.csv(document.graph_url, function(error, data) {
      data.forEach(function(d) {
        d.date = parseDate(d.date);
        d.close = +d.close;
      });

      // Scale the range of the data
      x.domain(d3.extent(data, function(d) {
        return d.date;
      }));
      y.domain([ 0, d3.max(data, function(d) {
        return d.close;
      }) ]);

      // Add the valueline path.
      svg.append('path')
        .attr('class', 'line')
        .attr('d', valueline(data));

      // Add the X Axis
      svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

      // Add the Y Axis
      svg.append('g')
        .attr('class', 'y axis')
        .call(yAxis);

    });

  }

  let loadingKudos = false;

  $(document).on('click', '.load-more', function() {

    if (loadingKudos) {
      return;
    }

    loadingKudos = true;
    var address = $('#preferred-address').prop('title');
    var link = $(this);
    var page = link.data('page');
    var request = link.data('request');
    var handle = link.data('handle');

    if (!handle) {
      return;
    }

    $.ajax({
      type: 'POST',
      url: '/lazy_load_kudos/',
      data: {
        'page': page,
        'request': request,
        'address': address,
        'handle': handle,
        'csrfmiddlewaretoken': '{{csrf_token}}' // from index.html
      },
      success: function(data) {
        loadingKudos = false;
        // if there are still more pages to load,
        // add 1 to the "Load More Posts" link's page data attribute
        // else hide the link
        if (data.has_next) {
          link.data('page', page + 1);
        } else {
          link.hide();
          $(window).off('scroll');
        }
        // append html to the posts div
        var elem = '#' + request;

        $(elem + ' div').first().append(data.kudos_html);
      },
      error: function(xhr, status, error) {
        loadingKudos = false;
        // shit happens friends!
      }
    });
  });
}(jQuery));

