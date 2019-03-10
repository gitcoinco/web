$(document).ready(function() {

  $('#kudos-section').on('click keypress', '.flip-card', e => {
    if ($(e.target).is('a')) {
      e.stopPropagation();
      return;
    }
    $(e.currentTarget).toggleClass('turn');
  });

  $('#kudos-section').on('click', '.pin_to_profile', e => {
  e.preventDefault();
  var pk = $(e.target).data('pk');
  var position = parseInt(prompt("Which position do you want to pin this kudos? (1-5)","1"));
  var is_invalid = isNaN(position) || position < 1 || position > 5;
  if(is_invalid){
    _alert('Herp Derp!  Invalid input');
  } else {
    var target_url = window.location.href.split('?')[0] + "?action=mutate_pinned_kudos&pk=" + pk + "&position=" + position;
    document.location.href = target_url;
  }
});

  

  setupTabs('#activity-tabs');

  const tabSection = document.querySelector('#activity-tabs-sections');
  const updateViewBtn = document.querySelector('#update-view-btn');
  let fetchInProgress = false;

  function updateView(ignoreScrollOffset) {
    window.setTimeout(updateView, 300);

    if (fetchInProgress) {
      return;
    }

    const activityContainer = document.querySelector('.tab-section.active .activities');
    const activityCount = parseInt(activityContainer.getAttribute('count')) || 0;
    const loadingImg = document.querySelector('.loading_img');

    if (activityContainer.children.length < activityCount) {
      updateViewBtn.style['visibility'] = 'visible';
    } else {
      updateViewBtn.style['visibility'] = 'hidden';
      return;
    }

    if (ignoreScrollOffset || window.scrollY >= tabSection.scrollHeight) {
      const activityName = activityContainer.id;
      let page = parseInt(activityContainer.getAttribute('page')) || 1;

      fetchInProgress = true;
      loadingImg.className = loadingImg.className.replace('hidden', 'visible');

      fetch(document.location.href + '?p=' + (++page) + '&a=' + activityName).then(
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
