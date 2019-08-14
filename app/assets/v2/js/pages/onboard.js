var onboard = {};
var current = 0;
var words = [];

if ($('.logged-in').length) {
  $('.nav-item.dropdown #navbarDropdown').css('visibility', 'visible');
  $('.nav_avatar').css('visibility', 'visible');
}

$('.js-select2').each(function() {
  $(this).select2({
    minimumResultsForSearch: Infinity
  });
});

// removes tooltip
if ($('#job').parent().css('display') !== 'none') {
  $('#job select').each(function(evt) {
    $('.select2-selection__rendered').tooltip('destroy');
  });
}

onboard.showTab = function(num) {
  $($('.step')[num]).addClass('block').outerWidth();
  $($('.step')[num]).addClass('show');

  if (num === 0) {
    $('#prev-btn').hide();
  } else {
    $('#prev-btn').show();
    window.history.pushState('', '', '/onboard/' + flow + '/' + $($('.step')[num]).attr('link'));
  }

  if (num === 2 || $($('.step')[num]).attr('link') === 'avatar') {
    $('.controls').hide();
  } else {
    $('.controls').show();
  }

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
    if (i <= currentStep)
      $(steps[i]).addClass('finish');
  }
};

document.alreadyFoundMetamask = false;
onboard.watchMetamask = function() {
  if (document.alreadyFoundMetamask) {
    return;
  } else if (typeof web3 == 'undefined') {
    $('.step #metamask').html(`
      <div class="locked">
        <a class="button button--primary" target="_blank" href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral">
          <img src="` + static_url + `v2/images/metamask.svg">
          <span>` + gettext('Install Metamask') + `</span>
        </a>
      </div>`
    );
  } else if (!web3.eth.coinbase) {
    $('.step #metamask').html(`
      <div class="locked">
        <a class="button button--primary" target="_blank" href="https://metamask.io/?utm_source=gitcoin.co&utm_medium=referral">
          <img src="` + static_url + `v2/images/metamask.svg">
          <span>` + gettext('Unlock Metamask') + `</span>
        </a>
      </div>`
    );
    if (current === 1) {
      $('#metamask-video').show();
    }
  } else {
    $('.step #metamask').html(
      '<div class="unlocked"><img src="' + static_url + 'v2/images/metamask.svg"><span class="mr-1">' +
      gettext('Unlocked') + '</span><i class="far fa-check-circle"></i></div><div class="font-body mt-3"><div class=col><label for=eth_address>' +
      gettext('Ethereum Payout Address') + '</label></div><div class="col"><input class="w-100 text-center" type=text id=eth_address name=eth_address placeholder="' +
      gettext('Ethereum Payout Address') + '"" value=' + web3.eth.coinbase + '></div></div>');
    if (current === 1) {
      document.alreadyFoundMetamask = true;
      $('.controls').show();
      $('#metamask-video').hide();
      $('#next-btn').on('click', function(e) {
        var eth_address = $('#eth_address').val();

        $.get('/onboard/contributor/', {eth_address: eth_address});
      });
    }
  }
};

onboard.getFilters = function(savedKeywords) {
  $('.suggested-tag input[type=checkbox]:checked + span i').removeClass('fa-plus').addClass('fa-check');
  $('.suggested-tag input[type=checkbox]:not(:checked) + span i').removeClass('fa-check').addClass('fa-plus');

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
    $('.suggested-tag input[type=checkbox]:checked + span i').removeClass('fa-plus').addClass('fa-check');
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

  if ($($('.step')[current]).attr('link') === 'skills') {
    var level = $('#experienceLevel').find(':selected').val();

    localStorage['experience_level'] = level;
    localStorage['referrer'] = 'onboard';
  }

  if ($($('.step')[current]).attr('link') === 'job') {
    save_job_status();
  }

  $(steps[current]).removeClass('show');
  $(steps[current]).removeClass('block');
  $('.alert').remove();

  current += n;
  if (current > steps.length - 1) {
    redirectURL();
  } else {
    onboard.showTab(current);
  }
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
  var url = '';

  if (flow === 'contributor') {
    save_job_status();
    url = '/explorer?q=' + words.join(',');
  } else if (flow === 'funder') {
    url = '/funding/new';
  } else if (flow === 'profile') {
    url = '/profile';
  }

  document.location.href = url;
};

localStorage['onboarded_funder'] = true;