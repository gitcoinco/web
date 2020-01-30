var localStorage;

try {
  localStorage = window.localStorage;
} catch (e) {
  localStorage = {};
}

const scrub = value => value.replace(/[!@#$%^&*(),.?":{}|<>]+/g, '');


var buildURI = function(custom_filters) {
  let uri = '';
  let _filters = [];

  if (custom_filters) {
    _filters = custom_filters;
  } else {
    _filters.push('ts_keywords');
  }

  _filters.forEach((filter) => {
    if (localStorage[filter] &&
      localStorage[filter] != 'any') {
        uri += (filter + '=' + localStorage[filter] + '&');
    }
  });

  return uri.slice(0, -1);
}

var storeFilters = function(value) {
  if (localStorage['ts_keywords']) {
    const ts_keywords = localStorage['ts_keywords'];
    const new_value = ',' + value;

    if (ts_keywords === value ||
      ts_keywords.indexOf(new_value) !== -1 ||
      ts_keywords.indexOf(value + ',') !== -1) {
        return;
    }
    
    localStorage['ts_keywords'] = ts_keywords + new_value;
  } else {
    localStorage['ts_keywords'] = value;
  }
}

var getFilters = function() {
  var _filters = [];

  if (localStorage['ts_keywords']) {
    localStorage['ts_keywords'].split(',').forEach(function(v, k) {
      _filters.push('<a class="filter-tag ts_keywords"><span>' + scrub(v) + '</span>' +
      '<i class="fas fa-times" onclick="removeFilter(\'ts_keywords\', \'' + scrub(v) + '\')"></i></a>');
    });
  }

  $('.filter-tags').html(_filters);
}

var removeFilter = function () {

}

var removeFilter = function(key, value) {
  if (key !== 'ts_keywords') {
    $('input[name="' + key + '"][value="' + value + '"]').prop('checked', false);
  } else {
    localStorage[key] = localStorage[key].replace(value, '').replace(',,', ',');

    // Removing the start and last comma to avoid empty element when splitting with comma
    localStorage[key] = localStorage[key].replace(/^,|,\s*$/g, '');
  }

  refreshActivities();
};

var refreshActivities = function () {
  var searchInput = $('#keywords')[0];

  if (searchInput && searchInput.value.length > 0) {
    storeFilters(searchInput.value.trim());
    searchInput.value = '';
    searchInput.blur();
  }

  getFilters();

  // fetch activities

  window.history.pushState('', '', window.location.pathname + window.location.search + '&' + buildURI());
}

$(document).ready(function() {
  refreshActivities();

  // gets multi part (ex: 10 hours 2 minutes 5 seconds) time
  var time_difference_broken_down = function(difference) {
    let remaining = ' now.. Refresh to view offer!';
    let prefix = ' in ';

    if (difference > 0) {
      const parts = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60)
      };

      remaining = Object.keys(parts)
        .map(part => {
          if (!parts[part])
            return;
          return `${parts[part]} ${part}`;
        })
        .join(' ');
    } else {
      return remaining;
    }
    return prefix + remaining;
  };

  $('.top_offer').click(function(e) {
    document.location = $(this).find('a.btn').attr('href');
  });

  // effects when an offer is clicked upon
  $('.offer a').click(function(e) {
    var speed = 500;

    $(this).addClass('clicked');
    $(this).find('#ribbon').effect('puff', speed, function() {
      $(this).find('#giftbox').effect('puff', speed);
    });
  });

  var get_redir_location = function(tab) {
    let trending = $('#trending').is(':checked') ? 1 : 0;

    return '/?tab=' + tab + '&trending=' + trending;
  };

  $('body').on('focus change paste keyup blur', '#keyword', function(e) {
    if ((e.keyCode == 13)) {
      e.preventDefault();
      document.location.href = get_redir_location('search-' + $('#keyword').val());
    }
  });

  $('body').on('click', '#trending', function(e) {
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
  });
  $('body').on('click', '.container .nav-link', function(e) {
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    e.preventDefault();
    setTimeout(function() {
      document.location.href = get_redir_location($('.nav-link.active').data('slug'));
    }, 10);
  });

  // updates expiry timers with countdowns
  var updateTimers = function() {
    $('.timer').each(function() {
      var time = $(this).data('time');
      var base_time = $(this).data('base_time');
      var counter = $(this).data('counter');

      if (!counter) {
        counter = 0;
      }
      counter += 1;
      $(this).data('counter', counter);
      var start_date = new Date(new Date(time).getTime() - (1000 * counter));
      var countdown = start_date - new Date(base_time);

      $(this).html(time_difference_broken_down(countdown));
    });
  };

  setInterval(updateTimers, 1000);

  // toggles the daily email sender
  $('#receive_daily_offers_in_inbox').on('change', function(e) {
    _alert('Your email subscription preferences have been updated', 'success', 2000);

    var url = '/api/v0.1/emailsettings/';
    var params = {
      'new_bounty_notifications': $(this).is(':checked'),
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };

    $.post(url, params, function(response) {
      // no message to be sent
    });
  });

  // clear any announcement
  $('.announce .remove').click(function() {
    $(this).parents('.announce').remove();
  });

   // search bar
   $('.townsquare_main').delegate('#new_search', 'click', function(e) {
    refreshActivities();
    e.preventDefault();
  });

  $('.search-area input[type=text]').keypress(function(e) {
    if (e.which == 13) {
      refreshActivities();
      e.preventDefault();
    }
  });

}(jQuery));
