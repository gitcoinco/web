/* eslint-disable no-loop-func */

var filters = [
  'experience_level',
  'project_length',
  'bounty_type',
  'bounty_filter',
  'moderation_filter',
  'network',
  'idx_status',
  'project_type',
  'permission_type',
  'misc'
];
var local_storage_keys = JSON.parse(JSON.stringify(filters));

local_storage_keys.push('keywords');

results_limit = 50;

var localStorage;

var explorer = { };

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

/**
 * Fetches all filters options from the URI
 */
var getActiveFilters = function() {

  if (window.location.search) {
    resetFilters();
  }
  let _filters = filters.slice();

  _filters.push('keywords', 'order_by');
  _filters.forEach(filter => {
    if (getParam(filter)) {
      localStorage[filter] = getParam(filter).replace(/^,|,\s*$/g, '');
    }
  });
};

/**
 * Build URI based on selected filter
 */
var buildURI = function() {
  let uri = '';
  let _filters = filters.slice();

  _filters.push('keywords', 'order_by');
  _filters.forEach((filter) => {
    if (localStorage[filter] &&
      localStorage[filter] != 'any') {
      uri += (filter + '=' + localStorage[filter] + '&');
    }
  });

  return uri.slice(0, -1);
};

/**
 * Updates localStorage with selected filters
 */
var save_sidebar_latest = function() {
  localStorage['order_by'] = $('#sort_option').val();

  filters.forEach((filter) => {
    localStorage[filter] = '';

    $('input[name="' + filter + '"]:checked').each(function() {
      localStorage[filter] += $(this).val() + ',';
    });

    localStorage[filter] = localStorage[filter].replace(/^,|,\s*$/g, '');
  });
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
  }

  getActiveFilters();

  if (localStorage['order_by']) {
    $('#sort_option').val(localStorage['order_by']);
    $('#sort_option').selectmenu().selectmenu('refresh');
  }

  filters.forEach((filter) => {
    if (localStorage[filter]) {
      localStorage[filter].split(',').forEach(function(val) {
        $('input[name="' + filter + '"][value="' + val + '"]').prop('checked', true);
      });

      if ($('input[name="' + filter + '"][value!=any]:checked').length > 0)
        $('input[name="' + filter + '"][value=any]').prop('checked', false);
    }
  });
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
  if (localStorage['keywords']) {
    const keywords = localStorage['keywords'];
    const new_value = ',' + value;

    if (keywords === value ||
        keywords.indexOf(new_value) !== -1 ||
        keywords.indexOf(value + ',') !== -1) {

      return;
    }
    localStorage['keywords'] = keywords + new_value;
  } else {
    localStorage['keywords'] = value;
  }

  $('.filter-tags').append('<a class="filter-tag keywords"><span>' + value + '</span>' +
    '<i class="fas fa-times" onclick="removeFilter(\'keywords\', \'' + value + '\')"></i></a>');
};

var getFilters = function() {
  var _filters = [];

  filters.forEach((filter) => {
    $.each($('input[name="' + filter + '"]:checked'), function() {
      if ($(this).attr('val-ui')) {
        _filters.push('<a class="filter-tag ' + filter + '"><span>' + $(this).attr('val-ui') + '</span>' +
          '<i class="fas fa-times" onclick="removeFilter(\'' + filter + '\', \'' + $(this).attr('value') + '\')"></i></a>');
      }
    });
  });

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, k) {
      _filters.push('<a class="filter-tag keywords"><span>' + v + '</span>' +
        '<i class="fas fa-times" onclick="removeFilter(\'keywords\', \'' + v + '\')"></i></a>');
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

  reset_offset();
  refreshBounties(null, 0, false, false);
};

var get_search_URI = function(offset) {
  var uri = '/api/v0.1/bounties/?';
  var keywords = '';

  filters.forEach((filter) => {
    var active_filters = [];

    $.each ($('input[name="' + filter + '"]:checked'), function() {
      if ($(this).val()) {
        active_filters.push($(this).val());
      }
    });

    var val = active_filters.toString();

    if ((filter === 'bounty_filter') && val) {
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

        if (_value !== 'any') {
          if (!uri.endsWith('?'))
            uri += '&';
          uri += _key + '=' + _value;
        }
      });

      // TODO: Check if value myself is needed for coinbase
      if (val === 'fulfilledByMe') {
        filter = 'bounty_owner_address';
        val = 'myself';
      }
    }

    if (val && val !== 'any' &&
      filter !== 'bounty_filter' &&
      filter !== 'bounty_owner_address') {
      if (!uri.endsWith('?'))
        uri += '&';
      uri += filter + '=' + val;
    }
  });

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, pos, arr) {
      keywords += v;
      if (arr.length > pos + 1) {
        keywords += ',';
      }
    });
  }

  if (keywords) {
    uri += '&raw_data=' + keywords;
  }

  var order_by = localStorage['order_by'];

  if (order_by) {
    uri += '&order_by=' + order_by;
  }
  uri += '&offset=' + offset;
  uri += '&limit=' + results_limit;
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

  show_stats = false; // TODO: xfr over to new stats API call
  if (show_stats) {
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
        fundingInfoEl.html('<span id="modifiers">Funded Issue</span><span id="stats" class="font-caption">(' + stats + ')</span>');
        break;
      default:
        matchesEl.html(num + gettext(' Matching Results'));
        fundingInfoEl.html('<span id="modifiers">Funded Issues</span><span id="stats" class="font-caption">(' + stats + ')</span>');
    }
  }
};

var trigger_scroll = debounce(function() {
  var scrollPos = $(document).scrollTop();
  var last_active_bounty = $('.bounty_row.result:last-child');

  if (last_active_bounty.length == 0) {
    return;
  }

  var window_height = $(window).height();
  var have_painted_all_bounties = false;// TODO
  var buffer = 500;
  var get_more = !have_painted_all_bounties && ((last_active_bounty.offset().top) < (scrollPos + buffer + window_height));

  if (get_more && !document.done_loading_results) {

    // move loading indicator
    var loading_html = $('.loading_img').clone().wrap('<p>').parent().html();

    $('.loading_img').remove();
    $('#bounties').append(loading_html);
    $('.loading_img').css('display', 'block');

    document.offset = parseInt(document.offset) + parseInt(results_limit);
    refreshBounties(null, document.offset, true, false);
  }
}, 200);

$(window).scroll(trigger_scroll);
$('body').bind('touchmove', trigger_scroll);

var reset_offset = function() {
  document.done_loading_results = false;
  document.offset = 0;
};

var refreshBounties = function(event, offset, append, do_save_search) {

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
  if (do_save_search) {
    if (!is_search_already_saved()) {
      save_search();
    }
  }
  paint_search_tabs();

  window.history.pushState('', '', '/explorer?' + buildURI());

  if (!append) {
    $('.nonefound').css('display', 'none');
    $('.loading').css('display', 'block');
    $('.bounty_row').remove();
  }
  // filter
  var uri = get_search_URI(offset);

  // analytics
  mixpanel.track('Refresh Bounties', { uri: uri });

  // Abort pending request if any subsequent request
  if (explorer.bounties_request && explorer.bounties_request.readyState !== 4) {
    explorer.bounties_request.abort();
  }

  explorer.bounties_request = $.get(uri, function(results, x) {
    results = sanitizeAPIResults(results);

    if (results.length === 0 && !append) {
      if (localStorage['referrer'] === 'onboard') {
        $('.no-results').removeClass('hidden');
        $('#dashboard-content').addClass('hidden');
      } else {
        $('.nonefound').css('display', 'block');
      }
    }

    document.last_bounty_rendered = 0;

    var html = renderBountyRowsFromResults(results, true);

    if (html) {
      $('#bounties').append(html);
    }

    document.done_loading_results = results.length < results_limit;

    $('div.bounty_row.result').each(function() {
      var href = $(this).attr('href');

      if (typeof $(this).changeElementType !== 'undefined') {
        $(this).changeElementType('a'); // hack so that users can right click on the element
      }

      $(this).attr('href', href);
    });

    if (localStorage['referrer'] === 'onboard') {
      $('.bounty_row').each(function(index) {
        if (index > 2)
          $(this).addClass('hidden');
      });
    }

    process_stats(results);
  }).fail(function() {
    if (explorer.bounties_request.readyState !== 0)
      _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'error');
  }).always(function() {
    $('.loading').css('display', 'none');
  });
};

window.addEventListener('load', function() {
  set_sidebar_defaults();
  reset_offset();
  refreshBounties(null, 0, false, false);
});

function getURLParams(k) {
  var p = {};

  location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(s, k, v) {
    p[k] = v;
  });
  return k ? p[k] : p;
}

/**
 * removed all filters from the sidebar search
 * resetKeyword : boolean
 */
var resetFilters = function(resetKeyword) {
  filters.forEach((filter) => {
    var tag = ($('input[name="' + filter + '"][value]'));

    for (var j = 0; j < tag.length; j++) {
      if (tag[j].value == 'any')
        $('input[name="' + filter + '"][value="any"]').prop('checked', true);
      else
        $('input[name="' + filter + '"][value="' + tag[j].value + '"]').prop('checked', false);
    }
  });

  if (resetKeyword && localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, k) {
      removeFilter('keywords', v);
    });
  }
};

(function() {
  if (localStorage['referrer'] === 'onboard') {
    $('#sidebar_container').addClass('invisible');
    $('#dashboard-title').addClass('hidden');
    $('#onboard-dashboard').removeClass('hidden');
    $('#onboard-footer').removeClass('hidden');
    resetFilters(true);
    $('input[name=idx_status][value=open]').prop('checked', true);
    $('.search-area input[type=text]').text(getURLParams('q'));

    $('#onboard-alert').click(function(e) {

      if (!$('.no-results').hasClass('hidden'))
        $('.nonefound').css('display', 'block');

      $('.bounty_row').each(function(index) {
        $(this).removeClass('hidden');
      });

      $('#onboard-dashboard').addClass('hidden');
      $('#onboard-footer').addClass('hidden');
      $('#sidebar_container').removeClass('invisible');
      $('#dashboard-title').removeClass('hidden');
      $('#dashboard-content').removeClass('hidden');

      localStorage['referrer'] = '';
      e.preventDefault();
    });
  } else {
    $('#dashboard-content').removeClass('hidden');
    $('#onboard-dashboard').addClass('hidden');
    $('#onboard-footer').addClass('hidden');
    $('#sidebar_container').removeClass('invisible');
    $('#dashboard-title').removeClass('hidden');
  }
})();

$(document).ready(function() {

  // Sort select menu
  $('#sort_option').selectmenu({
    select: function(event, ui) {
      reset_offset();
      refreshBounties(null, 0, false, true);
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
    resetFilters(true);
    reset_offset();
    refreshBounties(null, 0, false, true);
  });

  // search bar
  $('#bounties').delegate('#new_search', 'click', function(e) {
    reset_offset();
    refreshBounties(null, 0, false, true);
    e.preventDefault();
  });

  // search bar -- remove bounty
  $('#bounties').delegate('#search_nav li a', 'click', function(e) {
    var n = $(this).parents('li').data('num');

    remove_search(n);
    paint_search_tabs();
  });

  // search bar
  $('#bounties').delegate('#search_nav li span', 'click', function(e) {
    var n = $(this).parents('li').data('num');

    load_search(n);
    refreshBounties(null, 0, false, false);
  });


  $('.search-area input[type=text]').keypress(function(e) {
    if (e.which == 13) {
      reset_offset();
      refreshBounties(null, 0, false, true);
      e.preventDefault();
    }
  });

  // sidebar filters
  $('.sidebar_search input[type=radio], .sidebar_search label').change(function(e) {
    reset_offset();
    refreshBounties(null, 0, false, true);
    e.preventDefault();
  });

  // sidebar filters
  $('.sidebar_search input[type=checkbox], .sidebar_search label').change(function(e) {
    reset_offset();
    refreshBounties(null, 0, false, true);
    e.preventDefault();
  });
});


var get_this_search_name = function() {
  var names = [];
  var eles = $('.filter-tag');

  for (let i = 0; i < eles.length; i++) {
    var ele = eles[i];

    names.push(ele.text.toLowerCase());
  }
  names = names.join(',');
  return names;
};

var is_search_already_saved = function() {
  var this_search = get_this_search_name();

  for (let i = 0; i < 100; i++) {
    var new_key = '_name_' + i;
    var result = localStorage[new_key];

    if (typeof result != 'undefined') {
      if (this_search == result) {
        return true;
      }
    }
  }
  return false;
};

// search sidebar saving

// saves search info in local storage
var save_search = function() {
  if (typeof localStorage['searches'] == 'undefined') {
    localStorage['searches'] = '0';
  }
  searches = localStorage['searches'].split(',');
  max = parseInt(Math.max.apply(Math, searches));
  next = max + 1;
  searches = searches + ',' + next;
  localStorage['searches'] = searches;
  // save each key
  for (let i = 0; i < local_storage_keys.length; i++) {
    var key = local_storage_keys[i];
    let new_key = '_' + key + '_' + next;

    localStorage[new_key] = localStorage[key];
  }

  // save the name
  let new_key = '_name_' + next;

  localStorage[new_key] = get_this_search_name();

};

var get_search_tab_name = function(n) {
  var new_key = '_name_' + n;

  return localStorage[new_key];

};

var paint_search_tabs = function() {
  if (!localStorage['searches'])
    return;

  var container = $('#dashboard-title');
  var target = $('#search_nav');

  searches = localStorage['searches'].split(',');

  if (searches.length <= 1)
    return target.html('');

  var html = "<ul class='nav'><i class='fas fa-history'></i>";

  for (var i = 0; i < searches.length; i++) {
    var search_no = searches[i];
    var title = get_search_tab_name(search_no);

    if (title) {
      html += "<li class='nav-item' data-num='" + search_no + "'><span>" + title + '</span><a><i class="fas fa-times"></i></a></li>';
    }
  }
  html += '</ul>';
  target.html(html);
};


// gets available searches
var get_available_searches = function() {
  if (typeof localStorage['searches'] == 'undefined') {
    localStorage['searches'] = '';
  }
  return localStorage['searches'].split(',');
};

// loads search info from local storage
var load_search = function(n) {

  for (var i = 0; i < local_storage_keys.length; i++) {
    var key = local_storage_keys[i];
    var new_key = '_' + key + '_' + n;

    localStorage[key] = localStorage[new_key];
  }
};

// removes this search
var remove_search = function(n) {
  var is_last_element = ('0,' + n) == localStorage['searches'];

  if (is_last_element) {
    localStorage['searches'] = '0';
    return;
  }
  search_str = ',' + n + ',';
  replace_str = ',';
  localStorage['searches'] = localStorage['searches'].replace(search_str, replace_str);
  var key = '_name_' + n;

  localStorage.removeItem(key);
};

