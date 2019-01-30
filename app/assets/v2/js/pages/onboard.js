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

  if (num === 1 || num === 2 || $($('.step')[num]).attr('link') === 'avatar') {
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
    if (current === 1) {
      $('.controls').hide();
    }
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
      $('.controls').hide();
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

const save_job_status = function() {
  if (!document.contxt.github_handle) {
    _alert('No profile', 'error');
  }
  const formData = new FormData();
  const job_search_status = $('#jobStatus').find(':selected').val();
  const show_job_status = $('#showJobStatus').prop('checked');
  const job_type = $('input[name=jobType]:checked').val();
  const remote = $('#jobRemote:checked').val();
  const job_salary = $('#jobSalary').val();
  const job_cv = $('#jobCV')[0].files;

  formData.append('job_cv', job_cv[0], job_cv[0].name);
  formData.append('job_search_status', job_search_status);
  formData.append('show_job_status', show_job_status);
  formData.append('job_type', job_type);
  formData.append('locations', jobLocations);
  formData.append('remote', remote);
  formData.append('job_salary', job_salary);

  const profile = {
    url: '/api/v0.1/profile/' + document.contxt.github_handle + '/jobopportunity',
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    data: formData,
    processData: false,
    dataType: 'json',
    contentType: false
  };

  $.ajax(profile).done(function(response) {
    _alert(response.message, 'info');
  }).fail(function(error) {
    _alert(error, 'error');
  });
};

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

let jobLocations = [];
let autocomplete;

function initPlacecomplete() {
  let input = document.getElementById('jobLocation');

  var options = {
    types: ['(regions)']
  };

  autocomplete = new google.maps.places.Autocomplete(input, options);
  autocomplete.addListener('place_changed', function() {
    let place = autocomplete.getPlace();

    jobLocations.push(place);
    setLocations(jobLocations);
  });
}

const setLocations = (jobLocations) => {
  let locationsHtml = [];

  $.each(jobLocations, function(k, value) {
    locationsHtml.push(`<a class=filter-tag data-index=${k}><i class="fas fa-times"></i>${value.formatted_address}</a>`);
  });
  $('.locations').html(locationsHtml);
  $('#jobLocation').val('');
};

const removeLocations = (index) => {
  jobLocations.splice(index, 1);
};

$('.locations').on('click', '.filter-tag', function(e) {
  removeLocations($(this).data('index'));
  $(this).remove();
});

$('#jobSalary').on('change', function() {
  let currentValue = $(this).val();

  $(this).val(Number(currentValue.replace(',', '')).toLocaleString());
});


const checkFileSize = (elem, max_img_size) => {
  let input = document.getElementById(elem);

  if (input.files && input.files.length == 1) {
    if (input.files[0].size > max_img_size) {
      alert(`The file must be less than ${(max_img_size / 1024 / 1024).toFixed(2)}MB`);
      input.value = '';
      return false;
    }
  }
  return true;
};

$('#jobCV').on('change', () =>{
  checkFileSize('jobCV', 3144000);
});
