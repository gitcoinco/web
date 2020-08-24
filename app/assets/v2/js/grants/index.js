Vue.component('grant-card', {
  delimiters: [ '[[', ']]' ],
  props: [ 'grant', 'cred', 'token' ],
  methods: {
    get_clr_prediction: function(indexA, indexB) {
      if (this.grant.clr_prediction_curve) {
        return this.grant.clr_prediction_curve[indexA][indexB];
      }
    }
  }
});


$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });

  if ($('.grants_type_nav').length) {
    localStorage.setItem('last_grants_index', document.location.href);
    localStorage.setItem('last_grants_title', $('title').text().split('|')[0]);
  }
  if (document.location.href.indexOf('/cart') == -1) {
    localStorage.setItem('last_all_grants_index', document.location.href);
    localStorage.setItem('last_all_grants_title', $('title').text().split('|')[0]);
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

  // $(document).on('click keypress', '.flip-card', e => {
  //   if ($(e.target).is('a') || $(e.target).is('img')) {
  //     e.stopPropagation();
  //     return;
  //   }
  //   $(e.currentTarget).toggleClass('turn');
  // });

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

  if (document.getElementById('grants-showcase')) {
    var app = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#grants-showcase',
      data: {
        grants: [],
        page: 1,
        limit: 6,
        sort: 'weighted_shuffle',
        network: 'mainnet',
        keyword: '',
        state: 'active',
        category: '',
        credentials: false
      },
      methods: {
        fetchGrants: async function(page) {
          const params = new URLSearchParams({
            page: page || this.page,
            limit: this.limit,
            sort_option: this.sort,
            network: this.network,
            keyword: this.keyword,
            state: this.state,
            category: this.category
          }).toString();
          const response = await fetchData(`/grants/cards_info?${params}`);

          console.log(response);
          this.grants = response.grants;
          this.credentials = response.credentials;
        }
      },
      mounted() {
        this.fetchGrants(this.page);
      }
    });
  }

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

  const typeValue = $(this).data('type');
  const categoryValue = $(this).data('category');
  const params = { 'type': typeValue, 'category': categoryValue};

  updateMultipleParams(params);
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

$('#expand').on('click', () => {
  $('#expand').hide();
  $('#minimize').show();
  $('#sidebar_container form#filters').css({
    'height': 'auto',
    'display': 'inherit'
  });
});

$('#minimize').on('click', () => {
  $('#minimize').hide();
  $('#expand').show();
  $('#sidebar_container form#filters').css({
    'height': 0,
    'display': 'none'
  });
});

$(document).on('click', '.star-action', async(e) => {
  e.preventDefault();
  const element = (e.target.tagName === 'BUTTON') ? $(e.target) : $(e.target.parentElement);
  const grantId = element.data('grant');
  const favorite_url = `/grants/${grantId}/favorite`;

  let response = await fetchData(favorite_url, 'POST');

  if (response.action === 'follow') {
    element.find('i').addClass('fa');
    element.find('i').removeClass('far');
    element.find('span').text('Following');
    element.removeClass('text-muted');
  } else {
    element.find('i').removeClass('fa');
    element.find('i').addClass('far');
    element.find('span').text('Follow');
    element.addClass('text-muted');

    if (window.location.pathname === '/grants/following') {
      element.closest('.grant-card').hide();
    }
  }

  console.log(response);
});
