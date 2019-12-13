$(document).ready(function() {
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

  const syncComplete = res => {
    console.log('sync complete');
  }

  const openBox = callback => {
    window.ethereum.enable().then(addresses => {
      window.Box.openBox(addresses[0], window.ethereum, {}).then(box => {
        box.onSyncDone(syncComplete);
        window.box = box;
        console.log("openBox succeeded");
        callback(box);
      })
    })
  }

  const openSpace = (box, callback) => {
    const name = "GitCoin";
    window.currentSpace = name;
    const opts = {
      onSyncDone: () => {
        console.log('sync done in space', name)
        callback(box, box.spaces[name]);
      }
    }
    box.openSpace(name, opts).then(() => {

    })
  }

  const backupProfile = async space => {
    const profile_json = window.profile_json;
    // get public key-value
    const public_keys = Object.keys(profile_json).filter(k => k[0] !== '_');
    const public_values = public_keys.map(k => profile_json[k]);
    // get private key-value
    let private_keys = Object.keys(profile_json).filter(k => k[0] === '_');
    const private_values = private_keys.map(k => profile_json[k]);
    private_keys = private_keys.map(k => k.substring(1));

    space.public.setMultiple(public_keys, public_values).then(() => {
      console.log("sync to public space done")
    })
    space.private.setMultiple(private_keys, private_values).then(() => {
      console.log("sync to private space done")
    })

    // remove the unused key/value pairs from the space
    removeUnusedFields(space, public_keys, private_keys);
  }

  const removeUnusedFields = async (space, public_keys, private_keys) => {
    const public_data = await space.public.all();
    const private_data = await space.private.all();

    const unused_public_keys = Object.keys(public_data).filter(x => !public_keys.includes(x));
    const unused_private_keys = Object.keys(private_data).filter(x => !private_keys.includes(x));
    await removeFields(space.public, unused_public_keys);
    await removeFields(space.private, unused_private_keys);

    const count = unused_public_keys.length + unused_private_keys.length;
    console.log(`remove ${count} unused fields from space`, unused_public_keys, unused_private_keys);
  }

  const removeFields = async (subspace, keys) => {
    if (keys && keys.length > 0) {
      for (let x of keys) {
        await subspace.remove(x);
      }
    }
  }

  $("#sync-to-3box").on('click', function(event) {
    console.log("start sync data to 3box");

    // User is prompted to approve the messages inside their wallet (openBox() and openSpace()
    // methods via 3Box.js). This logs them in to 3Box.

    // 1. Open box and space
    // 2. Backing up my Gitcoin data to 3Box, inside of a "Gitcoin" space
    openBox(box => {
      openSpace(box, (box, space) => {
        console.log("backup data into space", space);
        backupProfile(space);
      });
    });
  })


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
}(jQuery));
