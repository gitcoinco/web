/* eslint-disable no-loop-func */
// helper functions
var technologies = [
  '.NET', 'ASP .NET', 'Angular', 'Backbone', 'Bootstrap', 'C', 'C#', 'C++', 'CSS', 'CSS3',
  'CoffeeScript', 'Dart', 'Django', 'Drupal', 'DynamoDB', 'ElasticSearch', 'Ember', 'Erlang', 'Express', 'Go', 'Groovy',
  'Grunt', 'HTML', 'Hadoop', 'Jasmine', 'Java', 'JavaScript', 'Jekyll', 'Knockout', 'LaTeX', 'Mocha', 'MongoDB',
  'MySQL', 'NoSQL', 'Node.js', 'Objective-C', 'Oracle', 'PHP', 'Perl', 'Polymer', 'Postgres', 'Python', 'R', 'Rails',
  'React', 'Redis', 'Redux', 'Ruby', 'SASS', 'Scala', 'Sqlite', 'Swift', 'TypeScript', 'Websockets', 'WordPress', 'jQuery'
];

var sidebar_keys = [
  'experience_level',
  'project_length',
  'bounty_type',
  'bounty_filter',
  'network',
  'idx_status',
  'tech_stack'
];

var localStorage;

try {
  localStorage = window.localStorage;
} catch (e) {
  localStorage = {};
}

function debounce(func, wait, immediate) {
  var timeout;

  return function() {
    var context = this;
    var args = arguments;
    var later = function() {
      timeout = null;
      if (!immediate)
        func.apply(context, args);
    };
    var callNow = immediate && !timeout;

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow)
      func.apply(context, args);
  };
}

// sets search information default
var save_sidebar_latest = function() {
  localStorage['order_by'] = $('#sort_option').val();

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];

    localStorage[key] = '';

    $('input[name="' + key + '"]:checked').each(function() {
      localStorage[key] += $(this).val() + ',';
    });

    // Removing the start and last comma to avoid empty element when splitting with comma
    localStorage[key] = localStorage[key].replace(/^,|,\s*$/g, '');
  }
};

// saves search information default
var set_sidebar_defaults = function() {
  // Special handling to support adding keywords from url query param
  var q = getParam('q');
  var keywords;

  if (q) {
    keywords = decodeURIComponent(q).replace(/^,|\s|,\s*$/g, '');

    if (localStorage['keywords']) {
      keywords.split(',').forEach(function(v, k) {
        if (localStorage['keywords'].indexOf(v) === -1) {
          localStorage['keywords'] += ',' + v;
        }
      });
    } else {
      localStorage['keywords'] = keywords;
    }

    window.history.replaceState(history.state, 'Issue Explorer | Gitcoin', '/explorer');
  }

  if (localStorage['order_by']) {
    $('#sort_option').val(localStorage['order_by']);
    $('#sort_option').selectmenu('refresh');
  }

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];

    if (localStorage[key]) {
      localStorage[key].split(',').forEach(function(v, k) {
        $('input[name="' + key + '"][value="' + v + '"]').prop('checked', true);
      });

      if ($('input[name="' + key + '"][value!=any]:checked').length > 0)
        $('input[name="' + key + '"][value=any]').prop('checked', false);
    }
  }
};

var set_filter_header = function() {
  var idxStatusEl = $('input[name=idx_status]:checked');
  var filter_status = idxStatusEl.attr('val-ui') ? idxStatusEl.attr('val-ui') : 'All';

  $('#filter').html(filter_status);
};

var toggleAny = function(event) {
  if (!event)
    return;
  var key = event.target.name;
  var anyOption = $('input[name="' + key + '"][value=any]');

  // Selects option 'any' when no filter is applied
  if ($('input[name="' + key + '"]:checked').length === 0) {
    anyOption.prop('checked', true);
    return;
  }
  if (event.target.value === 'any') {
    // Deselect other filters when 'any' is selected
    $('input[name="' + key + '"][value!=any]').prop('checked', false);
  } else {
    // Deselect option 'any' when another filter is selected
    anyOption.prop('checked', false);
  }
};

var addTechStackKeywordFilters = function(value) {
  var isTechStack = false;

  technologies.forEach(function(v, k) {
    if (v.toLowerCase() === value) {
      isTechStack = true;

      $('.filter-tags').append('<a class="filter-tag tech_stack"><span>' + value + '</span>' +
        '<i class="fa fa-times" onclick="removeFilter(\'tech_stack\', \'' + value + '\')"></i></a>');

      $('input[name="tech_stack"][value=' + value + ']').prop('checked', true);
    }
  });

  if (!isTechStack) {
    if (localStorage['keywords']) {
      localStorage['keywords'] += ',' + value;
    } else {
      localStorage['keywords'] += value;
    }

    $('.filter-tags').append('<a class="filter-tag keywords"><span>' + value + '</span>' +
      '<i class="fa fa-times" onclick="removeFilter(\'keywords\', \'' + value + '\')"></i></a>');
  }
};

var getFilters = function() {
  var _filters = [];

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];

    $.each($('input[name="' + key + '"]:checked'), function() {
      if ($(this).attr('val-ui')) {
        _filters.push('<a class="filter-tag ' + key + '"><span>' + $(this).attr('val-ui') + '</span>' +
          '<i class="fa fa-times" onclick="removeFilter(\'' + key + '\', \'' + $(this).attr('value') + '\')"></i></a>');
      }
    });
  }

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, k) {
      _filters.push('<a class="filter-tag keywords"><span>' + v + '</span>' +
        '<i class="fa fa-times" onclick="removeFilter(\'keywords\', \'' + v + '\')"></i></a>');
    });
  }

  $('.filter-tags').html(_filters);
};

var removeFilter = function(key, value) {
  if (key !== 'keywords') {
    $('input[name="' + key + '"][value="' + value + '"]').prop('checked', false);
  } else {
    localStorage['keywords'] = localStorage['keywords'].replace(value, '').replace(',,', ',');

    // Removing the start and last comma to avoid empty element when splitting with comma
    localStorage['keywords'] = localStorage['keywords'].replace(/^,|,\s*$/g, '');
  }

  refreshBounties();
};

var get_search_URI = function() {
  var uri = '/api/v0.1/bounties/?';
  var keywords = '';

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];
    var filters = [];

    $.each ($('input[name="' + key + '"]:checked'), function() {
      if (key === 'tech_stack' && $(this).val()) {
        keywords += $(this).val() + ',';
      } else if ($(this).val()) {
        filters.push($(this).val());
      }
    });

    var val = filters.toString();

    if ((key === 'bounty_filter') && val) {
      var values = val.split(',');

      values.forEach(function(_value) {
        var _key;

        if (_value === 'createdByMe') {
          _key = 'bounty_owner_github_username';
          _value = document.contxt.github_handle;
        } else if (_value === 'startedByMe') {
          _key = 'interested_github_username';
          _value = document.contxt.github_handle;
        } else if (_value === 'fulfilledByMe') {
          _key = 'fulfiller_github_username';
          _value = document.contxt.github_handle;
        }

        if (_value !== 'any')
          uri += _key + '=' + _value + '&';
      });

      // TODO: Check if value myself is needed for coinbase
      if (val === 'fulfilledByMe') {
        key = 'bounty_owner_address';
        val = 'myself';
      }
    }

    if (val !== 'any' &&
        key !== 'bounty_filter' &&
        key !== 'bounty_owner_address') {
      uri += key + '=' + val + '&';
    }
  }

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, pos, arr) {
      keywords += v;
      if (arr.length < pos + 1) {
        keywords += ',';
      }
    });
  }

  if (keywords) {
    uri += '&raw_data=' + keywords;
  }

  if (typeof web3 != 'undefined' && web3.eth.coinbase) {
    uri += '&coinbase=' + web3.eth.coinbase;
  } else {
    uri += '&coinbase=unknown';
  }

  var order_by = localStorage['order_by'];

  if (order_by) {
    uri += '&order_by=' + order_by;
  }

  return uri;
};

var process_stats = function(results) {
  var num = results.length;
  var worth_usdt = 0;
  var worth_eth = 0;
  var currencies_to_value = {};

  for (var i = 0; i < results.length; i++) {
    var result = results[i];

    var this_worth_usdt = Number.parseFloat(result['value_in_usdt']);
    var this_worth_eth = Number.parseFloat(result['value_in_eth']);

    if (this_worth_usdt) {
      worth_usdt += this_worth_usdt;
    }
    if (this_worth_eth) {
      worth_eth += this_worth_eth;
    }
    var token = result['token_name'];

    if (token !== 'ETH') {
      if (!currencies_to_value[token]) {
        currencies_to_value[token] = 0;
      }
      currencies_to_value[token] += Number.parseFloat(result['value_true']);
    }
  }

  worth_usdt = worth_usdt.toFixed(2);
  worth_eth = (worth_eth / Math.pow(10, 18)).toFixed(2);
  var stats = worth_usdt + ' USD, ' + worth_eth + ' ETH';

  for (var t in currencies_to_value) {
    if (Object.prototype.hasOwnProperty.call(currencies_to_value, t)) {
      stats += ', ' + currencies_to_value[t].toFixed(2) + ' ' + t;
    }
  }

  var matchesEl = $('#matches');
  var fundingInfoEl = $('#funding-info');

  switch (num) {
    case 0:
      matchesEl.html(gettext('No Results'));
      fundingInfoEl.html('');
      break;
    case 1:
      matchesEl.html(num + gettext(' Matching Result'));
      fundingInfoEl.html("<span id='modifiers'>Funded Issue</span><span id='stats' class='font-body'>(" + stats + ')</span>');
      break;
    default:
      matchesEl.html(num + gettext(' Matching Results'));
      fundingInfoEl.html("<span id='modifiers'>Funded Issues</span><span id='stats' class='font-body'>(" + stats + ')</span>');
  }
};

var paint_bounties_in_viewport = function(start, max) {
  document.is_painting_now = true;
  var num_bounties = document.bounties_html.length;

  for (var i = start; i < num_bounties && i < max; i++) {
    var html = document.bounties_html[i];

    document.last_bounty_rendered = i;
    $('#bounties').append(html);
  }

  $('div.bounty_row.result').each(function() {
    var href = $(this).attr('href');

    if (typeof $(this).changeElementType !== 'undefined') {
      $(this).changeElementType('a'); // hack so that users can right click on the element
    }

    $(this).attr('href', href);
  });
  document.is_painting_now = false;

  if (document.referrer.search('/onboard') != -1) {
    $('.bounty_row').each(function(index) {
      if (index > 2)
        $(this).addClass('hidden');
    });
  }
};

var trigger_scroll = debounce(function() {
  if (typeof document.bounties_html == 'undefined' || document.bounties_html.length == 0) {
    return;
  }
  var scrollPos = $(document).scrollTop();
  var last_active_bounty = $('.bounty_row.result:last-child');

  if (last_active_bounty.length == 0) {
    return;
  }

  var window_height = $(window).height();
  var have_painted_all_bounties = document.bounties_html.length <= document.last_bounty_rendered;
  var buffer = 500;
  var does_need_to_paint_more = !document.is_painting_now && !have_painted_all_bounties && ((last_active_bounty.offset().top) < (scrollPos + buffer + window_height));

  if (does_need_to_paint_more) {
    paint_bounties_in_viewport(document.last_bounty_rendered + 1, document.last_bounty_rendered + 6);
  }
}, 200);

$(window).scroll(trigger_scroll);
$('body').bind('touchmove', trigger_scroll);

var refreshBounties = function(event) {

  // Allow search for freeform text
  var searchInput = $('#keywords')[0];

  if (searchInput.value.length > 0) {
    addTechStackKeywordFilters(searchInput.value.trim());
    searchInput.value = '';
    searchInput.blur();
    $('.close-icon').hide();
  }

  save_sidebar_latest();
  set_filter_header();
  toggleAny(event);
  getFilters();

  $('.nonefound').css('display', 'none');
  $('.loading').css('display', 'block');
  $('.bounty_row').remove();

  // filter
  var uri = get_search_URI();

  // analytics
  var params = { uri: uri };

  mixpanel.track('Refresh Bounties', params);

  // order
  $.get(uri, function(results) {
    results = sanitizeAPIResults(results);

    if (results.length === 0) {
      $('.nonefound').css('display', 'block');
    }

    document.is_painting_now = false;
    document.last_bounty_rendered = 0;
    document.bounties_html = [];

    for (var i = 0; i < results.length; i++) {
      // setup
      var result = results[i];
      var related_token_details = tokenAddressToDetails(result['token_address']);
      var decimals = 18;

      if (related_token_details && related_token_details.decimals) {
        decimals = related_token_details.decimals;
      }

      var divisor = Math.pow(10, decimals);

      result['rounded_amount'] = Math.round(result['value_in_token'] / divisor * 100) / 100;
      var is_expired = new Date(result['expires_date']) < new Date() && !result['is_open'];

      // setup args to go into template
      if (typeof web3 != 'undefined' && web3.eth.coinbase == result['bounty_owner_address']) {
        result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">mine</span></a>';
      } else if (result['fulfiller_address'] !== '0x0000000000000000000000000000000000000000') {
        result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">' + result['status'] + '</span></a>';
      }

      result.action = result['url'];
      result['title'] = result['title'] ? result['title'] : result['github_url'];


      result['p'] = ((result['experience_level'] ? result['experience_level'] : 'Unknown Experience Level') + ' &bull; ');

      if (result['status'] === 'done')
        result['p'] += 'Done';
      if (result['fulfillment_accepted_on']) {
        result['p'] += ' ' + timeDifference(new Date(), new Date(result['fulfillment_accepted_on']), false, 60 * 60);
      } else if (result['status'] === 'started') {
        result['p'] += 'Started';
        result['p'] += ' ' + timeDifference(new Date(), new Date(result['fulfillment_started_on']), false, 60 * 60);
      } else if (result['status'] === 'submitted') {
        result['p'] += 'Submitted';
        if (result['fulfillment_submitted_on']) {
          result['p'] += ' ' + timeDifference(new Date(), new Date(result['fulfillment_submitted_on']), false, 60 * 60);
        }
      } else if (result['status'] == 'cancelled') {
        result['p'] += 'Cancelled';
        if (result['canceled_on']) {
          result['p'] += ' ' + timeDifference(new Date(), new Date(result['canceled_on']), false, 60 * 60);
        }
      } else if (is_expired) {
        var time_ago = timeDifference(new Date(), new Date(result['expires_date']), true);

        result['p'] += ('Expired ' + time_ago + ' ago');
      } else {
        var opened_when = timeDifference(new Date(), new Date(result['web3_created']), true);

        var timeLeft = timeDifference(new Date(), new Date(result['expires_date']));
        var expiredExpires = new Date() < new Date(result['expires_date']) ? 'Expires' : 'Expired';
        var softOrNot = result['can_submit_after_expiration_date'] ? 'Soft ' : '';

        result['p'] += ('Opened ' + opened_when + ' ago, ' + softOrNot + expiredExpires + ' ' + timeLeft);
      }

      result['watch'] = 'Watch';

      // render the template
      var tmpl = $.templates('#result');
      var html = tmpl.render(result);

      document.bounties_html[i] = html;
    }

    paint_bounties_in_viewport(0, 10);

    process_stats(results);
  }).fail(function() {
    _alert({message: 'got an error. please try again, or contact support@gitcoin.co'}, 'error');
  }).always(function() {
    $('.loading').css('display', 'none');
  });
};

window.addEventListener('load', function() {
  set_sidebar_defaults();
  refreshBounties();
});

var getNextDayOfWeek = function(date, dayOfWeek) {
  var resultDate = new Date(date.getTime());

  resultDate.setDate(date.getDate() + (7 + dayOfWeek - date.getDay() - 1) % 7 + 1);
  return resultDate;
};

function getURLParams(k) {
  var p = {};

  location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(s, k, v) {
    p[k] = v;
  });
  return k ? p[k] : p;
}

var resetFilters = function() {
  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];
    var tag = ($('input[name="' + key + '"][value]'));

    for (var j = 0; j < tag.length; j++) {
      if (tag[j].value == 'any')
        $('input[name="' + key + '"][value="any"]').prop('checked', true);
      else
        $('input[name="' + key + '"][value="' + tag[j].value + '"]').prop('checked', false);
    }
  }
};

(function() {
  if (document.referrer.search('/onboard') != -1) {
    $('#sidebar_container').addClass('invisible');
    $('#dashboard-title').addClass('hidden');
    $('#onboard-dashboard').removeClass('hidden');
    resetFilters();
    $('input[name=idx_status][value=open]').prop('checked', true);
    $('.search-area input[type=text]').text(getURLParams('q'));
    document.referrer = '';

    $('#onboard-alert').click(function(e) {
      $('.bounty_row').each(function(index) {
        $(this).removeClass('hidden');
      });
      $('#onboard-dashboard').addClass('hidden');
      $('#sidebar_container').removeClass('invisible');
      $('#dashboard-title').removeClass('hidden');
      e.preventDefault();
    });
  } else {
    $('#onboard-dashboard').addClass('hidden');
    $('#sidebar_container').removeClass('invisible');
    $('#dashboard-title').removeClass('hidden');
  }
})();

$(document).ready(function() {

  // Sort select menu
  $('#sort_option').selectmenu({
    select: function(event, ui) {
      refreshBounties();
      event.preventDefault();
    }
  });

  // TODO: DRY
  function split(val) {
    return val.split(/,\s*/);
  }

  function extractLast(term) {
    return split(term).pop();
  }

  technologies.forEach(function(v, k) {
    $('#tech-stack-options').append(
      '<div class="checkbox_container">' +
        '<input name="tech_stack" id="' + v.toLowerCase() + '" type="checkbox" value="' + v.toLowerCase() + '" val-ui="' + v + '"/>' +
        '<span class="checkbox"></span>' +
        '<div class="filter-label">' +
          '<label for="' + v.toLowerCase() + '">' + v + '</label>' +
        '</div>' +
      '</div>'
    );
  });

  // Handle search input clear
  $('.close-icon')
    .on('click', function(e) {
      e.preventDefault();
      $('#keywords').val('');
      $(this).hide();
    });

  $('#keywords')
    .on('input', function() {
      if ($(this).val()) {
        $('.close-icon').show();
      } else {
        $('.close-icon').hide();
      }
    })
    // don't navigate away from the field on tab when selecting an item
    .on('keydown', function(event) {
      if (event.keyCode === $.ui.keyCode.TAB && $(this).autocomplete('instance').menu.active) {
        event.preventDefault();
      }
    })
    .autocomplete({
      minLength: 0,
      source: function(request, response) {
        // delegate back to autocomplete, but extract the last term
        response($.ui.autocomplete.filter(document.keywords, extractLast(request.term)));
      },
      focus: function() {
        // prevent value inserted on focus
        return false;
      },
      select: function(event, ui) {
        var terms = split(this.value);

        $('.close-icon').hide();

        // remove the current input
        terms.pop();

        // add the selected item
        terms.push(ui.item.value);

        // add placeholder to get the comma-and-space at the end
        terms.push('');

        this.value = '';

        addTechStackKeywordFilters(ui.item.value);

        return false;
      }
    });

  // sidebar clear
  $('.dashboard #clear').click(function(e) {
    e.preventDefault();
    resetFilters();
    refreshBounties();
  });

  // search bar
  $('#bounties').delegate('#new_search', 'click', function(e) {
    refreshBounties();
    e.preventDefault();
  });

  $('.search-area input[type=text]').keypress(function(e) {
    if (e.which == 13) {
      refreshBounties();
      e.preventDefault();
    }
  });

  // sidebar filters
  $('.sidebar_search input[type=radio], .sidebar_search label').change(function(e) {
    refreshBounties();
    e.preventDefault();
  });

  // sidebar filters
  $('.sidebar_search input[type=checkbox], .sidebar_search label').change(function(e) {
    refreshBounties(e);
    e.preventDefault();
  });

  // email subscribe functionality
  $('.save_search').click(function(e) {
    e.preventDefault();
    $('#save').remove();
    var url = '/sync/search_save';

    setTimeout(function() {
      $.get(url, function(newHTML) {
        $(newHTML).appendTo('body').modal();
        $('#save').append("<input type='hidden' name='raw_data' value='" + get_search_URI() + "'>");
        $('#save_email').focus();
      });
    }, 300);
  });

  var emailSubscribe = function() {
    var email = $('#save input[type=email]').val();
    var raw_data = $('#save input[type=hidden]').val();
    var is_validated = validateEmail(email);

    if (!is_validated) {
      _alert({ message: gettext('Please enter a valid email address.') }, 'warning');
    } else {
      var url = '/sync/search_save';

      $.post(url, {
        email: email,
        raw_data: raw_data
      }, function(response) {
        var status = response['status'];

        if (status == 200) {
          _alert({message: gettext("You're in! Keep an eye on your inbox for the next funding listing.")}, 'success');
          $.modal.close();
        } else {
          _alert({message: response['msg']}, 'error');
        }
      });
    }
  };

  $('body').delegate('#save input[type=email]', 'keypress', function(e) {
    if (e.which == 13) {
      emailSubscribe();
      e.preventDefault();
    }
  });
  $('body').delegate('#save a', 'click', function(e) {
    emailSubscribe();
    e.preventDefault();
  });
});
