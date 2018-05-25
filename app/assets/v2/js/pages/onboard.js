var onboard = {};
var steps = [ 'github', 'metamask', 'avatar', 'skills' ];
var current = 0;
var words = [];

$('.js-select2').each(function() {
  $(this).select2();
});

onboard.showTab = function(num) {
  $($('.step')[num]).addClass('block').outerWidth();
  $($('.step')[num]).addClass('show');
  window.history.pushState('', '', '/onboard/' + $($('.step')[num]).attr('link'));

  if (num == 0)
    $('#prev-btn').hide();
  else
    $('#prev-btn').show();

  if (num == ($('.step').length) - 1) {
    $('#next-btn').html(gettext('Done'));
    $('#next-btn').attr('onclick', 'redirectURL()');
  } else if (num > ($('.step').length) - 1) {
    $('#next-btn').hide();
    $('#next-btn').attr('onclick', 'changeStep(1))');
  } else {
    $('#next-btn').removeClass('completed');
    $('#next-btn').html(gettext('Next'));
    $('#next-btn').attr('onclick', 'changeStep(1)');
  }
  onboard.highlightStep(num);
  $('#next-btn').addClass('completed');
};

onboard.highlightStep = function(currentStep) {
  var steps = $('.step-state');

  for (i = 0; i < steps.length; i++) {
    if (i < currentStep)
      $(steps[i]).addClass('finish');
    $(steps[i]).removeClass('active');
  }
  $(steps[currentStep]).addClass('active');
};

onboard.watchMetamask = function() {
  if (typeof web3 == 'undefined') {
    $('.step #metamask').html(`
      <div class="locked">
        <a class="button button--primary" target="_blank" href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral">
          <img src="/static/v2/images/metamask.svg" %}>
          <span>` + gettext('Install Metamask') + `</span>
        </a>
      </div>`
    );
  } else if (!web3.eth.coinbase) {
    $('.step #metamask').html(`
      <div class="locked">
        <a class="button button--primary" target="_blank" href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral">
          <img src="/static/v2/images/metamask.svg" %}>
          <span>` + gettext('Unlock Metamask') + `</span>
        </a>
      </div>`
    );
  } else {
    $('.step #metamask').html('<div class="unlocked"><img src="/static/v2/images/metamask.svg" %}><span>' + gettext('Unlocked') + '</span></div>');
  }
};

onboard.getFilters = function(savedKeywords) {
  $('.suggested-tag input[type=checkbox]:checked + span svg').attr('data-icon', 'check');
  $('.suggested-tag input[type=checkbox]:not(:checked) + span svg').attr('data-icon', 'plus');

  var _filters = [];
  var _words = [];
  var search_keywords = $('#keywords').val();

  if (search_keywords && search_keywords != '') {
    search_keywords.split(',').forEach(function(word) {
      _words.push(word);
      _filters.push('<a class=filter-tag><i class="fas fa-check"></i>' + word + '</a>');
    });
  }

  if (savedKeywords) {
    $.each(savedKeywords, function(k, value) {
      if (keywords.includes(value.toLowerCase())) {
        $('input[type=checkbox][name=tech-stack][value="' + value.toLowerCase() + '"]').prop('checked', true);
      } else {
        if ($('#keywords').val() != '') {
          $('#keywords').val($('#keywords').val() + ',');
        }

        $('#keywords').val($('#keywords').val() + value.toLowerCase());
        _words.push(value.toLowerCase());
        _filters.push('<a class=filter-tag><i class="fas fa-check"></i>' + value.toLowerCase() + '</a>');
      }
    });
  }

  $.each($('input[type=checkbox][name=tech-stack]:checked'), function() {
    var value = $(this).attr('value');

    _words.push(value);
  });

  if (_filters.length == 0)
    $('#selected-skills').css('display', 'none');
  else
    $('#selected-skills').css('display', 'inherit');

  $('.filter-tags').html(_filters);
  words = [...new Set(_words)];
  // TODO: Save Preferences
  var settings = {
    url: '/settings/matching',
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    data: JSON.stringify({
      'keywords': 'JavaScript,CCoffeeScript,CSS,HTML',
      'submit': 'Go',
      'github': 'thelostone-mc'
    })
  };

  $.ajax(settings).done(function(response) {
    // TODO : Update keywords for user profile
  }).fail(function(error) {
    // TODO: Handle Error
  });
};

var changeStep = function(n) {
  if (current == 0 && n == -1)
    return;

  var steps = $('.step');

  $(steps[current]).removeClass('show');
  $(steps[current]).removeClass('block');

  current += n;
  onboard.showTab(current);
};

steps.forEach(function(step, index) {
  if (window.location.pathname.endsWith(step))
    current = index;
});

onboard.showTab(current);

onboard.watchMetamask();
setInterval(onboard.watchMetamask, 2000);

var keywords = [ 'css', 'solidity', 'python', 'javascript', 'ruby', 'django',
  'java', 'html', 'test', 'design' ];
var suggested_tags = [];

keywords.forEach(function(keyword) {
  suggested_tags.push(
    `<label class="suggested-tag">
        <input name="tech-stack" type="checkbox"
          value="` + keyword + `">
        <span class="text">
          <i class="fas fa-plus"></i>` + keyword + `
        </span>
      </label>`
  );
});

$('#skills #suggested-tags').html(suggested_tags);

if ($('.navbar #navbarDropdown').html()) {
  var url = '/api/v0.1/profile/' + $('.navbar #navbarDropdown').html().trim() + '/keywords';

  $.get(url, function(response) {
    onboard.getFilters(response.keywords);
  });
}

$('.suggested-tag input[type=checkbox]').change(function(e) {
  onboard.getFilters();
});

$('.search-area input[type=text]').keypress(function(e) {
  if (e.which == 13) {
    onboard.getFilters();
    e.preventDefault();
  }
});

var redirectURL = function() {
  var level = $('#experienceLevel').find(':selected').val();

  localStorage['experience_level'] = level;
  var url = '/explorer?q=' + words.join(',');

  localStorage['referrer'] = 'onboard';
  document.location.href = url;
};