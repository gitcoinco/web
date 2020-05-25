$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });

  if ($('.grants_type_nav').length) {
    localStorage.setItem('last_grants_index', document.location.href);
    localStorage.setItem('last_grants_title', $('title').text().split('|')[0]);
  }

  $('#network').select2({
    minimumResultsForSearch: Infinity
  });

  $(document).on('click', '.grant-item', function() {
    $(this).find('img').each(function() {
      var src_url = $(this).data('src');

      $(this).attr('src', src_url);
    });
  });

  searchGrant();
  populateFilters();

  $('.select2-selection__rendered').removeAttr('title');

  $(document).on('click keypress', '.flip-card', e => {
    if ($(e.target).is('a') || $(e.target).is('img')) {
      e.stopPropagation();
      return;
    }
    $(e.currentTarget).toggleClass('turn');
  });

  waitforWeb3(() => {
    let _network = $('#grant-network').html();
    let links = $('.etherscan_link');

    etherscanUrlConvert(links, _network);
  });

  window.addEventListener('scroll', function() {
    if ($('.activity_stream').length && $('.activity_stream').isInViewport()) {
      $('#skip').addClass('hidden');
    } else {
      $('#skip').removeClass('hidden');
    }

  });

});

const etherscanUrlConvert = (elem, network) => {
  elem.each(function() {
    $(this).attr('href', get_etherscan_url($(this).attr('href'), network));
  });
};

const searchGrant = () => {
  $('#sort_option').on('change', function(e) {
    updateParams('sort_option', $('#sort_option').val());
  });

  $('#network').on('change', function(e) {
    updateParams('network', $('#network').val());
  });

  $('#search_form').on('submit', (e) => {
    e.preventDefault();
    updateParams('keyword', $('#keyword').val());
  });
};

const populateFilters = () => {
  const sort = getURLParams('sort_option');
  const network = getURLParams('network');
  const keyword = getURLParams('keyword') ? getURLParams('keyword').replace('%20', ' ') : null;

  if (sort)
    $('#sort_option').val(getURLParams('sort_option')).trigger('change');
  if (network)
    $('#network').val(getURLParams('network')).trigger('change');
  if (keyword)
    $('#keyword').val(keyword);
};


$('.grants_nav a').on('click', function(event) {
  event.preventDefault();
  if ($(this).attr('href')) {
    document.location.href = $(this).attr('href');
    return;
  }
  const queryParam = $(this).data('type');
  const queryParamValue = $(this).data('value');

  updateParams(queryParam, queryParamValue);
});

var glow_skip = function() {
  setTimeout(function() {
    $('#skip').animate({color: '#999'}, {duration: 1000});
    setTimeout(function() {
      $('#skip').animate({color: '#bbb'}, {duration: 2000});
    }, 1500);
  }, 1000);
};

setInterval(glow_skip, 5000);
glow_skip();

$(document).ready(function() {
  $('.selected').parents('.accordion').trigger('click');
});