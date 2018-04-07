var current = 0;
var words = [];

$('.js-select2').each(function() {
  $(this).select2();
});

var showTab = function(num) {
  $($('.step')[num]).addClass('block').outerWidth();
  $($('.step')[num]).addClass('show');

  if (num == 0)
    $('#prev-btn').hide();
  else
    $('#prev-btn').show();

  if (num == ($('.step').length) - 1) {
    $('#next-btn').html('Finish');
    $('#next-btn').attr('onclick', 'redirectURL()');
  } else if (num > ($('.step').length) - 1) {
    $('#next-btn').hide();
    $('#next-btn').attr('onclick', 'changeStep(1))');
  } else {
    $('#next-btn').html('Next');
    $('#next-btn').attr('onclick', 'changeStep(1)');
  }
  highlightStep(num);
};

var changeStep = function(n) {
  if (current == 0 && n == -1)
    return;

  var steps = $('.step');

  $(steps[current]).removeClass('show');
  $(steps[current]).removeClass('block');

  current += n;
  showTab(current);
};


function highlightStep(currentStep) {
  var steps = $('.step-state');

  for (i = 0; i < steps.length; i++) {
    if (i < currentStep)
      $(steps[i]).addClass('finish');
    $(steps[i]).removeClass('active');
  }
  $(steps[currentStep]).addClass('active');
}

showTab(current);

if (typeof web3 == 'undefined') {
  $('.step #metamask span').text('Install Metamask');
} else if (!web3.eth.coinbase) {
  $('.step #metamask span').text('Unlock Metamask');
} else {
  // TODO: Refresh on update
  $('.step #metamask').css('margin-top', '2em');
  $('.step #metamask').css('margin-bottom', '1em');
  $('.step #metamask').html('<div class="unlocked"><img src="/static/v2/images/metamask.svg" %}><span>Unlocked</span></div>');
}

var watch_web3_status = function() {

  if (!document.listen_for_web3_iterations) {
    document.listen_for_web3_iterations = 1;
  } else {
    document.listen_for_web3_iterations += 1;
  }

  if (typeof web3 == 'undefined') {
    $('.step #metamask span').text('Install Metamask');
  } else if (!web3.eth.coinbase) {
    $('.step #metamask span').text('Unlock Metamask');
  } else {
    web3.eth.getBalance(web3.eth.coinbase, function(errors, result) {
      if (typeof result != 'undefined') {
        document.balance = result.toNumber();
      }
    });

    web3.version.getNetwork((error, netId) => {
      if (error)
        $('.step #metamask span').text('Install Metamask');
    });
  }
};

var keywords = [ 'css', 'solidity', 'python', 'javascript', 'ruby', 'django', 'java', 'elixir' ];
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

$('#step-3 #suggested-tags').html(suggested_tags);

$('.suggested-tag input[type=checkbox]').change(function(e) {
  getFilters();
});

$('.search-area input[type=text]').keypress(function(e) {
  if (e.which == 13) {
    getFilters();
    e.preventDefault();
  }
});

var getFilters = function() {
  var _filters = [];
  var _words = [];
  var search_keywords = $('#keywords').val();

  if (search_keywords && search_keywords != '') {
    search_keywords.split(',').forEach(function(word) {
      _words.push(word);
      _filters.push('<a class=filter-tag>' + word +
        '<i class="fas fa-times" onclick="removeFilter(\'' + word + '\')"></i></a>');
    });
  }

  $.each($('input[type=checkbox][name=tech-stack]:checked'), function() {
    var value = $(this).attr('value');

    _words.push(value);
    _filters.push('<a class=filter-tag>' + value +
      '<i class="fas fa-times" onclick="removeFilter(\'' + value + '\')"></i></a>');
  });

  if (_filters.length == 0)
    $('#selected-skills').css('display', 'none');
  else
    $('#selected-skills').css('display', 'inherit');

  $('.filter-tags').html(_filters);
  words = [...new Set(_words)];
};

var removeFilter = function(value) {
  $('input[name=tech-stack][value=' + value + ']').prop('checked', false);
  getFilters();
};

var redirectURL = function() {
  var level = $('#experienceLevel').find(':selected').text();
  var url = '/explorer?q=' + words.join(',') + '&experience_level=' + level;
  // TODO : Figure out how to set experience filter post re-direction to explorer

  localStorage['experience_level'] = level;
  document.location.href = url;
};