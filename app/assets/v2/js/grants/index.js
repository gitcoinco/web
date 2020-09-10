Vue.component('grant-card', {
  delimiters: [ '[[', ']]' ],
  props: [ 'grant', 'cred', 'token', 'view', 'short', 'show_contributions', 'contributions', 'toggle_following' ],
  methods: {
    get_clr_prediction: function(indexA, indexB) {
      if (this.grant.clr_prediction_curve && this.grant.clr_prediction_curve.length) {
        return this.grant.clr_prediction_curve[indexA][indexB];
      }
    },
    getContributions: function(grantId) {
      return this.contributions[grantId] || [];
    },
    toggleFollowingGrant: async function(grantId, event) {
      event.preventDefault();

      const favorite_url = `/grants/${grantId}/favorite`;
      let response = await fetchData(favorite_url, 'POST');

      if (response.action === 'follow') {
        this.grant.favorite = true;
      } else {
        this.grant.favorite = false;
      }

      return true;
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

  $('#wall_of_love .show_more_wall_of_love').click(function(e) {
    $('#wall_of_love .hidden').removeClass('hidden');
    $(this).remove();
    e.preventDefault();
  });

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

});

Vue.component('grant-sidebar', {
  props: [ 'filter_grants', 'grant_types', 'type', 'selected_category', 'keyword', 'following', 'set_type',
    'idle_grants', 'show_contributions'
  ],
  data: function() {
    return {
      search: this.keyword,
      show_filters: true
    };
  },
  methods: {
    toggleFollowing: function(state, event) {
      event.preventDefault;
      this.filter_grants({following: state});
    },
    toggleIdle: function(state, event) {
      event.preventDefault;
      this.filter_grants({idle_grants: state});
    },
    toggleContributionView: function(state, event) {
      event.preventDefault;
      this.filter_grants({show_contributions: state});
    }
  }
});
if (document.getElementById('grants-showcase')) {

  var appGrants = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#grants-showcase',
    data: {
      grants: [],
      page: 1,
      limit: 6,
      sort: 'weighted_shuffle',
      network: 'rinkeby',
      keyword: document.keyword,
      current_type: document.current_type,
      idle_grants: document.idle_grants,
      following: document.following,
      state: 'active',
      category: document.selected_category,
      credentials: false,
      grant_types: [],
      contributions: {},
      show_contributions: document.show_contributions,
      lock: false,
      view: localStorage.getItem('grants_view') || 'grid',
      shortView: true
    },
    methods: {
      setView: function(mode, event) {
        event.preventDefault();
        localStorage.setItem('grants_view', mode);
        this.view = mode;
      },
      setCurrentType: function(currentType, q) {
        this.current_type = currentType;

        if (this.current_type === 'all') {
          window.history.pushState('', '', `/grants/?${q || ''}`);
        } else {
          window.history.pushState('', '', `/grants/${this.current_type}?${q || ''}`);
        }
      },
      filter_grants: function(filters) {
        if (filters.type !== null && filters.type !== undefined) {
          this.current_type = filters.type;
        }
        if (filters.category !== null && filters.category !== undefined) {
          this.category = filters.category;
        }
        if (filters.keyword !== null && filters.keyword !== undefined) {
          this.keyword = filters.keyword;
        }
        if (filters.following !== null && filters.following !== undefined) {
          this.following = filters.following;
        }
        if (filters.idle_grants !== null && filters.idle_grants !== undefined) {
          this.idle_grants = filters.idle_grants;
        }
        if (filters.sort !== null && filters.sort !== undefined) {
          this.sort = filters.sort;
        }
        if (filters.show_contributions !== null && filters.show_contributions !== undefined) {
          this.show_contributions = filters.show_contributions;
        }

        this.page = 1;
        const query_elements = {};

        if (this.category && this.current_type !== 'all') {
          query_elements['category'] = this.category;
        }

        if (this.keyword) {
          query_elements['keyword'] = this.keyword;
        }
        if (this.idle_grants) {
          query_elements['idle'] = this.idle_grants;
        }
        if (this.following) {
          query_elements['following'] = this.following;
        }
        if (this.show_contributions) {
          query_elements['only_contributions'] = this.show_contributions;
        }
        if (this.sort !== 'weighted_shuffle') {
          query_elements['sort'] = this.sort;
        }
        const q = $.param(query_elements);

        this.setCurrentType(this.current_type, q);
        this.fetchGrants(this.page);
      },
      fetchGrants: async function(page, append_mode) {
        if (this.lock)
          return;

        this.lock = true;

        const base_params = {
          page: page || this.page,
          limit: this.limit,
          sort_option: this.sort,
          network: this.network,
          keyword: this.keyword,
          state: this.state,
          category: this.category,
          type: this.current_type
        };

        if (this.following) {
          base_params['following'] = this.following;
        }

        if (this.idle_grants) {
          base_params['idle'] = this.idle_grants;
        }

        if (this.show_contributions) {
          base_params['only_contributions'] = this.show_contributions;
        }

        const params = new URLSearchParams(base_params).toString();
        const response = await fetchData(`/grants/cards_info?${params}`);

        if (append_mode) {
          this.grants = this.grants.concat(response.grants);
        } else {
          this.grants = response.grants;
        }

        this.credentials = response.credentials;
        this.grant_types = response.grant_types;
        this.contributions = response.contributions;

        this.lock = false;
        return this.grants;
      },
      scroll: async function(event) {
        const scrollHeight = $(document).height();
        const scrollPos = $(window).height() + $(window).scrollTop();
        let vm = this;

        if (((scrollHeight - 300) >= scrollPos) / scrollHeight == 0) {
          const grants = await vm.fetchGrants(vm.page + 1, true);

          if (grants && grants.length) {
            vm.page = vm.page + 1;
          }
        }
      },
      // toggleFollowingGrant: async function(grantId, event) {
      //   event.preventDefault();

      //   const favorite_url = `/grants/${grantId}/favorite`;
      //   let response = await fetchData(favorite_url, 'POST');

      //   console.log(favorite_url);
      //   if (response.action === 'follow') {
      //     this.$set(this.grants[grantId], 'favorite', true);
      //   } else {
      //     this.$set(this.grants[grantId], 'favorite', false);
      //   }

      //   return true;
      // }
    },
    mounted() {
      let vm = this;

      this.fetchGrants(this.page);
      this.scroll();

      $('#sort_option2').select2({
        minimumResultsForSearch: Infinity,
        templateSelection: function(data, container) {
          // Add custom attributes to the <option> tag for the selected option
          vm.filter_grants({sort: data.id});

          return data.text;
        }
      });
    }
  });
}

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

$(document).on('click', '.following-action', async(e) => {
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
