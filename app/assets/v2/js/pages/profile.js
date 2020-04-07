$(document).ready(function() {
  $('#profile-tabs button').on('click', function() {
    document.location = $(this).attr('href');
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
          if (response.status === 200) {
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

  $(document).on('click', '.load-more', function() {
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
        // if there are still more pages to load,
        // add 1 to the "Load More Posts" link's page data attribute
        // else hide the link
        if (data.has_next) {
          link.data('page', page + 1);
        } else {
          link.hide();
        }
        // append html to the posts div
        var elem = '#' + request;

        $(elem + ' div').first().append(data.kudos_html);
      },
      error: function(xhr, status, error) {
        // shit happens friends!
      }
    });
  });

  $('body').each(function(index) {
  $(this).on('click', '.tab-projects__item #edit-portfolio-item', function() {
    var id = this.getAttribute("data-id")
    var portfolio_url = $('#portfolio_url').val()
    var portfolio_title = $('#portfolio_title').text()
    var portfolio_tags = $('#portfolio_tags').val()
    $("#id").val(id)
    $("#project_title").val(portfolio_title)
    $("#URL").val(portfolio_url)
    $("#tags").val(portfolio_tags)
    $("#submit").val("Update changes")
  });

  $('.tab-projects__item').each(function(index) {
    $(this).on('click', '#remove-portfolio-item', function() {
      var portfolio_id = this.getAttribute("data-id");
      var csrf_token = $('input[name="csrfmiddlewaretoken"]').attr('value')
      $.ajax({
        type: 'POST',
        url: "/api/v0.1/profile/remove_profile_portfolio",
        data: {
          method: "delete",
          portfolio_id,
          csrfmiddlewaretoken: csrf_token
        },
        success: function(data) {
          if (data.status === 200) {
            location.reload();
            _alert(
              { message: gettext('Portfolio item has been removed.') },
              'success'
            );
          } else {
            _alert(
              { message: gettext('An error occurred. Please try again.') },
              'error'
            );
          }
        },
        error: function(xhr, status, error) {
          // you know what to do!
        }
      })
    })
  });
});
}(jQuery));