let grantsNumPages = '';
let grantsHasNext = false;
let numGrants = '';


$(document).ready(() => {

  if ($('.grants_type_nav').length) {
    localStorage.setItem('last_grants_index', document.location.href);
    localStorage.setItem('last_grants_title', $('title').text().split('|')[0]);
  }
  if (document.location.href.indexOf('/cart') == -1) {
    localStorage.setItem('last_all_grants_index', document.location.href);
    localStorage.setItem('last_all_grants_title', $('title').text().split('|')[0]);
  }

  window.addEventListener('scroll', function() {
    if ($('.activity_stream').length && $('.activity_stream').isInViewport()) {
      $('#skip').addClass('hidden');
    } else {
      $('#skip').removeClass('hidden');
    }

  });

  // toggleStyle(document.current_style);
});

// Vue.component('grant-sidebar', {
//   props: [
//     'filter_grants', 'grant_types', 'type', 'selected_category', 'keyword', 'following', 'set_type',
//     'idle_grants', 'show_contributions', 'query_params', 'round_num', 'sub_round_slug', 'customer_name',
//     'featured'
//   ],
//   data: function() {
//     return {
//       search: this.keyword,
//       show_filters: false,
//       handle: document.contxt.github_handle
//     };
//   },
//   methods: {
//     toggleFollowing: function(state, event) {
//       event.preventDefault;
//       this.filter_grants({following: state});
//     },
//     toggleIdle: function(state, event) {
//       event.preventDefault;
//       this.filter_grants({idle_grants: state});
//     },
//     toggleContributionView: function(state, event) {
//       event.preventDefault;
//       this.filter_grants({show_contributions: state});
//     },
//     toggleMyGrants: function(state, event) {
//       let me = state ? 'me' : 'all';

//       event.preventDefault;
//       this.filter_grants({type: me, category: '', keyword: ''});
//     },
//     isMobileDevice: function() {
//       return window.innerWidth < 576;
//     },
//     toggleMyCollections: function(state, event) {
//       let me = state ? {type: 'collections', keyword: this.handle} : {type: 'all', keyword: ''};

//       this.filter_grants(me);

//       this.search = me.keyword;
//     },
//     filterLink: function(params) {

//       return this.filter_grants(params);
//     },
//     searchKeyword: function() {
//       if (this.timeout) {
//         clearTimeout(this.timeout);
//       }

//       this.timeout = setTimeout(() => {
//         this.filter_grants({keyword: this.search});
//       }, 1000);
//     },
//     onResize: function() {
//       if (!this.isMobileDevice() && this.show_filters !== null) {
//         this.show_filters = null;
//       } else if (this.isMobileDevice() && this.show_filters === null) {
//         this.show_filters = false;
//       }
//     }
//   },
//   mounted() {
//     window.addEventListener('resize', this.onResize);
//   }
// });
if (document.getElementById('grants-showcase')) {
  const baseParams = {
    page: 1,
    limit: 6,
    sort_option: 'weighted_shuffle',
    network: 'mainnet',
    // keyword: this.keyword,
    state: 'active',
    collections_page: 1,
    grant_types: [],
    grant_tags: [],
    tenants: [],
    idle: true

  };

  const grantRegions = [
    { 'name': 'north_america', 'label': 'North America'},
    { 'name': 'oceania', 'label': 'Oceania'},
    { 'name': 'latin_america', 'label': 'Latin America'},
    { 'name': 'europe', 'label': 'Europe'},
    { 'name': 'africa', 'label': 'Africa'},
    { 'name': 'middle_east', 'label': 'Middle East'},
    { 'name': 'india', 'label': 'India'},
    { 'name': 'east_asia', 'label': 'East Asia'},
    { 'name': 'southeast_asia', 'label': 'Southeast Asia'}
  ];

  const grantTenants = [
    {'name': 'ETH', 'label': 'Eth'},
    {'name': 'ZCASH', 'label': 'Zcash'},
    {'name': 'ZIL', 'label': 'Zil'},
    {'name': 'CELO', 'label': 'Celo'},
    {'name': 'POLKADOT', 'label': 'Polkadot'},
    {'name': 'HARMONY', 'label': 'Harmony'},
    {'name': 'KUSAMA', 'label': 'Kusama'},
    {'name': 'BINANCE', 'label': 'Binance'},
    {'name': 'RSK', 'label': 'Rsk'},
    {'name': 'ALGORAND', 'label': 'Algorand'}
  ];

  // const grant_tags = [
  //   {'name': 'ETH', 'label': 'Eth'},
  //   {'name': 'ZCASH', 'label': 'Zcash'},
  //   {'name': 'ZIL', 'label': 'Zil'},
  //   {'name': 'CELO', 'label': 'Celo'},
  //   {'name': 'POLKADOT', 'label': 'Polkadot'},
  //   {'name': 'HARMONY', 'label': 'Harmony'},
  //   {'name': 'KUSAMA', 'label': 'Kusama'},
  //   {'name': 'BINANCE', 'label': 'Binance'},
  //   {'name': 'RSK', 'label': 'Rsk'},
  //   {'name': 'ALGORAND', 'label': 'Algorand'}
  // ];



  // let sort = getParam('sort');

  // if (!sort) {
  //   sort = 'weighted_shuffle';
  // }
  var appGrants = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#grants-showcase',
    data: {
      activePage: document.activePage,
      grants: [],
      clrData: {},
      grantRegions: grantRegions,
      grantTenants: grantTenants,
      grant_tags: [],
      grant: {},
      collectionsPage: 1,
      show_active_clrs: window.localStorage.getItem('show_active_clrs') != 'false',
      network: document.network,
      keyword: document.keyword,
      current_type: document.current_type,
      idle_grants: document.idle_grants,
      following: document.following,
      featured: document.featured,
      state: 'active',
      category: document.selected_category,
      credentials: false,
      grant_types: [],
      contributions: {},
      collections: [],
      show_contributions: document.show_contributions,
      lock: false,
      view: localStorage.getItem('grants_view') || 'grid',
      shortView: true,
      bottom: false,
      cart_lock: false,
      collection_id: document.collection_id,
      // round_num: document.round_num,
      // clr_round_pk: document.clr_round_pk,
      // sub_round_slug: document.sub_round_slug,
      // customer_name: document.customer_name,
      activeCollection: null,
      grantsNumPages,
      grantsHasNext,
      numGrants,
      regex_style: {},
      params: Object.assign({}, baseParams),
      tagsOptions: [],
    },
    methods: {
      toggleStyle: function(style) {

        if (!style) {
          return;
        }

        // let banner;

        // if (style.bg) {
        //   banner = `url("${style.bg }") center top / ${style.size || ''} ${style.color || ''} no-repeat`;
        // } else {
        //   banner = `url("${ style.banner_image }") center  no-repeat`;
        // }
        // $('#grant-hero-img').css('background', banner);
        // if (style.background_image) {
        //   $('#grant-background-image-mount-point').css('background-image', style.background_image);
        // }

        if (style.inline_css) {
          $('.page-styles').last().text(style.inline_css);
        } else {
          $('.page-styles').last().text('');
        }
      },
      toggleActiveCLRs() {
        this.show_active_clrs = !this.show_active_clrs;
        window.localStorage.setItem('show_active_clrs', this.show_active_clrs);
      },
      setView: function(mode, event) {
        event.preventDefault();
        localStorage.setItem('grants_view', mode);
        this.view = mode;
      },
      setCurrentType: function(currentType) {
        this.current_type = currentType;

        if (this.current_type === 'collections') {
          this.clearSingleCollection();
        }

        this.updateURI();
      },
      fetchClrGrants: async function() {
        let vm = this;
        let url = 'http://localhost:8000/api/v0.1/grants_clr/';
        let getClr = await fetch(url, {cache: "force-cache"});
        let clrJson = await getClr.json();

        vm.clrData = clrJson;
      },
      // updateURI: function() {
      //   let vm = this;
      //   const q = vm.getQueryParams();

      //   // if (vm.round_num) {
      //   //   let uri = `/grants/clr/${vm.round_num}/`;

      //   //   if (vm.sub_round_slug && !vm.customer_name) {
      //   //     uri = `/grants/clr/${vm.round_num}/${vm.sub_round_slug}/`;
      //   //   }

      //   //   if (!vm.sub_round_slug && vm.customer_name) {
      //   //     uri = `/grants/clr/${vm.customer_name}/${vm.round_num}/`;
      //   //   }

      //   //   if (vm.sub_round_slug && vm.customer_name) {
      //   //     uri = `/grants/clr/${vm.customer_name}/${vm.round_num}/${vm.sub_round_slug}/`;
      //   //   }

      //   //   if (this.current_type === 'all') {
      //   //     window.history.pushState('', '', `${uri}?${q || ''}`);
      //   //   } else {
      //   //     window.history.pushState('', '', `${uri}?type=${this.current_type}&${q || ''}`);
      //   //   }
      //   // } else {
      //     let uri = '/grants/explorer/';

      //     if (this.current_type === 'all') {
      //       window.history.pushState('', '', `${uri}?${q || ''}`);
      //     } else {
      //       window.history.pushState('', '', `${uri}${this.current_type}?${q || ''}`);
      //     }
      //   // }

      //   if (this.current_type === 'activity') {
      //     const triggerTS = function() {
      //       const activeElement = $('.infinite-more-link');

      //       if (activeElement.length) {
      //         $('.infinite-more-link').click();
      //       } else {
      //         setTimeout(triggerTS, 1000);
      //       }
      //     };

      //     setTimeout(triggerTS, 1000);
      //   }
      // },

      changeBanner: function() {
        this.regex_style = document.all_routing_policies &&
          document.all_routing_policies.find(policy => {
            return new RegExp(policy.url_pattern).test(window.location.href);
          });
        this.toggleStyle(this.regex_style || document.current_style);
      },
      clearSingleCollection: function() {
        this.grants = [];
        this.collections = [];
        this.collection_id = null;
        this.activeCollection = null;
        this.params.page = 1;
        this.updateURI();
        this.fetchGrants();
      },
      showSingleCollection: function(collectionId) {
        this.collection_id = collectionId;
        this.collections = [];
        this.keyword = '';
        this.grants = [];
        this.params.page = 1;
        this.current_type = 'collections';
        this.updateURI();
        this.fetchGrants();
      },

      resetFilters: function() {
        let vm = this;

        console.log(baseParams)
        vm.params = Object.assign({}, baseParams);
        console.log(baseParams)
        vm.fetchGrants();

      },
      changeQuery: function(query) {
        let vm = this;

        for (let key in query) {
          console.log(key)
          vm.$set(vm.params, key, query[key]);
        }
        vm.fetchGrants();
      },
      getUrlParams: function() {
        let vm = this;

        const url = new URL(location.href);
        const params = new URLSearchParams(url.search);
        // for(var [key, value] of params.entries()) {
        //   vm.params[key] = value;
        // }

        for (let p of params) {
          if (typeof vm.params[p[0]] === 'object') {
            if (p[1].length > 0) {
              vm.params[p[0]] = p[1].split(',');
            } else {
              vm.$delete(vm.params[p[0]]);
            }
          } else {
            vm.params[p[0]] = p[1];
          }
        }
      },
      fetchGrants: async function(page, append_mode) {
        let vm = this;

        if (page) {
          vm.params.page = page;
        }

        // let urlParams = new URLSearchParams(window.location.search);
        let searchParams = new URLSearchParams(vm.params);
        console.log(searchParams.toString());
        window.history.replaceState({}, '', `${location.pathname}?${searchParams}`);

        if (this.lock)
          return;

        this.lock = true;

        const getGrants = await fetchData(`/grants/cards_info?${searchParams.toString()}`);

        if (!append_mode) {
          vm.grants = [];
        }
        getGrants.grants.forEach(function(item) {
          vm.grants.push(item);
        });

        if (this.collection_id) {
          if (getGrants.collections.length > 0) {
            this.activeCollection = getGrants.collections[0];
          }
        } else if (this.current_type === 'collections') {
          getGrants.collections.forEach(function(item) {
            vm.collections.push(item);
          });
        } else {
          vm.collections = getGrants.collections;
        }

        vm.credentials = getGrants.credentials;
        vm.grant_types = getGrants.grant_types;
        vm.contributions = getGrants.contributions;

        vm.grantsNumPages = getGrants.num_pages;
        vm.grantsHasNext = getGrants.has_next;
        vm.numGrants = getGrants.count;
        vm.changeBanner();

        if (vm.grantsHasNext) {
          vm.params.page = ++vm.params.page;
        } else {
          vm.params.page = 1;
        }

        vm.lock = false;

        return vm.grants;
      },
      scrollEnd: async function(event) {
        let vm = this;

        const scrollY = window.scrollY;
        const visible = document.documentElement.clientHeight;
        const pageHeight = document.documentElement.scrollHeight - 500;
        const bottomOfPage = visible + scrollY >= pageHeight;

        if (bottomOfPage || pageHeight < visible) {
          if (vm.grantsHasNext) {
            vm.fetchGrants(vm.params.page, true);
            vm.grantsHasNext = false;
          }
        }
      },
      addAllToCart: async function() {
        if (this.cart_lock)
          return;

        this.cart_lock = true;

        const base_params = {
          no_pagination: true,
          sort_option: this.params.sort_option,
          network: this.params.network,
          keyword: this.params.keyword,
          state: this.params.state,
          grant_tags: this.params.category,
          grant_types: this.current_type
        };

        if (this.clr_round_pk) {
          base_params['clr_round'] = this.clr_round_pk;
        }

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
        const getGrants = await fetchData(`/grants/bulk_cart?${params}`);


        (getGrants.grants || []).forEach((grant) => {
          CartData.addToCart(grant, true);
        });

        showSideCart();
        _alert(`Congratulations, ${getGrants.grants.length} ${getGrants.grants.length > 1 ? 'grants were' : 'grants was'} added to your cart!`, 'success');
        this.cart_lock = false;
      },
      removeCollection: async function({collection, grant, event}) {
        const getGrants = await fetchData(`/grants/v1/api/collections/${collection.id}/grants/remove`, 'POST', {
          'grant': grant.id
        });

        this.grants = getGrants.grants;
      },
      tagSearch(search, loading) {
        const vm = this;

        // if (search.length < 3) {
        //   return;
        // }
        loading(true);
        vm.getTag(loading, search);

      },
      getTag: async function(loading, search) {
        console.log(search);
        const vm = this;
        const myHeaders = new Headers();
        const url = `/api/v0.1/grants_tag/?name=${escape(search)}`;

        myHeaders.append('X-Requested-With', 'XMLHttpRequest');
        return new Promise(resolve => {

          fetch(url, {
            credentials: 'include',
            headers: myHeaders
          }).then(res => {
            res.json().then(json => {
              vm.$set(vm, 'tagsOptions', json);

              resolve();
            });
            if (loading) {
              loading(false);
            }
          });
        });
      },
    },
    computed: {
      currentCLR() {
        let vm = this;
        if (!vm.clrData.results)
          return;

        return vm.clrData?.results.find(item => {
          return item.sub_round_slug == vm.params?.sub_round_slug;
        })
      },
      isGrantExplorer() {
        return (this.activePage == 'grants_explorer');
      },
      isGrantCollectionExplorer() {
        return this.current_type === 'collections';
      },
      isUserLogged() {
        let vm = this;

        if (document.contxt.github_handle) {
          return true;
        }
      }

    },
    beforeMount() {
      window.addEventListener('scroll', () => {
        this.bottom = this.scrollEnd();
      }, false);
    },
    beforeDestroy() {
      window.removeEventListener('scroll', () => {
        this.bottom = this.scrollEnd();
      });
    },
    mounted() {
      let vm = this;

      vm.getUrlParams();
      vm.fetchClrGrants();
      vm.fetchGrants(vm.params.page);
    }
  });
}

// $(document).ready(function() {
//   $('.selected').parents('.accordion').trigger('click');
// });

// $('#expand').on('click', () => {
//   $('#expand').hide();
//   $('#minimize').show();
//   $('#sidebar_container form#filters').css({
//     'height': 'auto',
//     'display': 'inherit'
//   });
// });

// $('#minimize').on('click', () => {
//   $('#minimize').hide();
//   $('#expand').show();
//   $('#sidebar_container form#filters').css({
//     'height': 0,
//     'display': 'none'
//   });
// });

// $(document).on('click', '.following-action', async(e) => {
//   e.preventDefault();
//   const element = (e.target.tagName === 'BUTTON') ? $(e.target) : $(e.target.parentElement);
//   const grantId = element.data('grant');
//   const favorite_url = `/grants/${grantId}/favorite`;

//   let response = await fetchData(favorite_url, 'POST');

//   if (response.action === 'follow') {
//     element.find('i').addClass('fa');
//     element.find('i').removeClass('far');
//     element.find('span').text('Following');
//     element.removeClass('text-muted');
//   } else {
//     element.find('i').removeClass('fa');
//     element.find('i').addClass('far');
//     element.find('span').text('Follow');
//     element.addClass('text-muted');

//     if (window.location.pathname === '/grants/following') {
//       element.closest('.grant-card').hide();
//     }
//   }
// });
