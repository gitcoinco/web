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
    me: false,
    sort_option: 'weighted_shuffle',
    network: 'mainnet',
    // keyword: this.keyword,
    state: 'active',
    profile: false,
    collections_page: 1,
    grant_regions: [],
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
      collectionsPage: null,
      cart_data_count: CartData.length(),
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
      sub_round_slug: false,
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
      tabIndex: null,
      tabSelected: undefined,
      loadingCollections: false,
      searchVisible: false,
      searchParams: undefined,
      observer: null,
      observed: null,
      sticky_active: false
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
      fetchClrGrants: async function() {
        let vm = this;
        let url = '/api/v0.1/grants_clr/';
        let getClr = await fetch(url);
        let clrJson = await getClr.json();

        vm.clrData = clrJson;
      },

      changeBanner: function() {
        this.regex_style = document.all_routing_policies &&
          document.all_routing_policies.find(policy => {
            return new RegExp(policy.url_pattern).test(window.location.href);
          });
        this.toggleStyle(this.regex_style || document.current_style);
      },
      resetFilters: function() {
        let vm = this;

        console.log(baseParams);
        vm.params = Object.assign({}, baseParams);
        console.log(baseParams);
        vm.fetchGrants();

      },
      changeQuery: function(query) {
        let vm = this;

        vm.$set(vm, 'params', {...vm.params, ...query});

        if (vm.tabSelected === 'grants') {
          vm.fetchGrants();
        } else {
          vm.updateUrlParams();

        }
      },
      filterCollection: function(collectionId) {
        let vm = this;

        vm.params = Object.assign({}, baseParams);

        vm.changeQuery({collection_id: collectionId});
        vm.tabIndex = 0;
      },
      getUrlParams: function() {
        let vm = this;

        const url = new URL(location.href);
        const params = new URLSearchParams(url.search);

        const param_is_array = [ 'grant_regions', 'tenants', 'grant_types', 'grant_tags' ];

        // loop through all URL params
        for (let p of params) {
          const param_key = p[0];
          const param_value = p[1];

          if (typeof vm.params[param_key] === 'object') {
            if ((param_value.length > 0)) {
              vm.params[param_key] = param_value.split(',');
            } else {
              vm.$delete(vm.params[param_key]);
            }
          } else if (param_is_array.includes(param_key)) {
            vm.params[param_key] = param_value.split(',');
          } else if ([ 'true', 'false' ].includes(param_value)) {
            vm.params[param_key] = param_value == 'true';
          } else {
            vm.params[param_key] = param_value;
          }
        }
      },
      updateUrlParams: function() {
        let vm = this;

        vm.searchParams = new URLSearchParams(vm.params);

        window.history.replaceState({}, '', `${location.pathname}?${vm.searchParams}`);
      },
      fetchGrants: async function(page, append_mode) {
        let vm = this;

        if (page) {
          vm.params.page = page;
        }

        // let urlParams = new URLSearchParams(window.location.search);
        // let searchParams = new URLSearchParams(vm.params);

        await vm.updateUrlParams();

        if (this.lock)
          return;

        this.lock = true;
        const getGrants = await fetchData(`/grants/cards_info?${vm.searchParams.toString()}`);

        if (!append_mode) {
          vm.grants = [];
        }
        getGrants.grants.forEach(function(item) {
          vm.grants.push(item);
        });

        // if (this.params.collection_id) {
        //   if (getGrants.collections.length > 0) {
        //     this.activeCollection = getGrants.collections[0];
        //   }
        // } else if (this.current_type === 'collections') {
        //   getGrants.collections.forEach(function(item) {
        //     vm.collections.push(item);
        //   });
        // } else {
        //   vm.collections = getGrants.collections;
        // }

        vm.credentials = getGrants.credentials;
        vm.grant_types = getGrants.grant_types;
        vm.contributions = getGrants.contributions;

        vm.grantsNumPages = getGrants.num_pages;
        vm.grantsHasNext = getGrants.has_next;
        vm.numGrants = getGrants.count;
        vm.changeBanner();

        if (vm.grantsHasNext) {
          vm.params.page = ++vm.params.page;
        }

        this.updateCartData({
          detail: {
            list: CartData.loadCart()
          }
        });

        vm.lock = false;

        return vm.grants;
      },
      tabChange: function(input) {
        let vm = this;

        vm.tabSelected = vm.$refs.grantstabs.tabs[input].id;
        console.log(vm.tabSelected);
        vm.changeQuery({tab: vm.tabSelected});
        vm.unobserveFilter();
        vm.params.profile = false;
        if (vm.tabSelected === 'collections') {
          vm.updateUrlParams();

          this.fetchCollections();
        } else {
          this.fetchGrants(1);
          setTimeout(() => vm.observeFilter());
        }
      },
      loadTab: function() {
        let vm = this;
        let loadParams = new URLSearchParams(document.location.search);
        const tabStrings = [
          {'index': 0, 'string': 'grants'},
          {'index': 1, 'string': 'collections'}
        ];

        console.log(loadParams.get('tab'));
        if (loadParams.has('tab')) {
          vm.tabSelected = loadParams.get('tab');
          console.log(tabStrings.filter(tab => tab.string === vm.tabSelected)[0].index);
          vm.tabIndex = tabStrings.filter(tab => tab.string === vm.tabSelected)[0].index;
          console.log(vm.tabIndex);
        }

        if (vm.tabSelected === 'collections') {
          vm.updateUrlParams();
          this.fetchCollections();
        } else {
          this.fetchGrants();
        }
      },
      fetchCollections: async function(append_mode) {
        let vm = this;

        if (vm.loadingCollections)
          return;

        vm.loadingCollections = true;

        // vm.updateUrlParams();

        let url = `/api/v0.1/grants_collections/?${(vm.params.profile ? 'profile=' + vm.params.profile : '')}`;

        if (vm.collectionsPage) {
          url = vm.collectionsPage;
        }
        let getCollections = await fetch(url);
        let collectionsJson = await getCollections.json();

        console.log(collectionsJson);

        if (append_mode) {
          vm.collections = [ ...vm.collections, ...collectionsJson.results ];
        } else {
          vm.collections = collectionsJson.results;
        }


        vm.collectionsPage = collectionsJson.next;
        vm.loadingCollections = false;

      },
      scrollEnd: async function(event) {
        let vm = this;

        const scrollY = window.scrollY;
        const visible = document.documentElement.clientHeight;
        const pageHeight = document.documentElement.scrollHeight - 500;
        const bottomOfPage = visible + scrollY >= pageHeight;
        const topOfPage = visible + scrollY <= pageHeight;
        // console.log(bottomOfPage, pageHeight, visible, topOfPage);

        if (bottomOfPage || pageHeight < visible) {
          if (vm.params.tab === 'collections' && vm.collectionsPage) {
            vm.fetchCollections(true);
          } else if (vm.grantsHasNext) {
            vm.fetchGrants(vm.params.page, true);
            vm.grantsHasNext = false;
          }
        }
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
      updateCartData: function(e) {
        const grants_in_cart = (e && e.detail && e.detail.list && e.detail.list) || [];
        const grant_ids_in_cart = grants_in_cart.map((grant) => grant.grant_id);

        this.cart_data_count = grants_in_cart.length;
        this.grants.forEach((grant) => {
          vm.$set(grant, 'isInCart', (grant_ids_in_cart.indexOf(String(grant.id)) !== -1));
        });
      },
      scrollBottom: function() {
        this.bottom = this.scrollEnd();
      },
      closeDropdown(ref) {
        // Close the menu and (by passing true) return focus to the toggle button
        this.$refs[ref].hide(true);
      },
      observeFilter() {
        // ensure the ref is in the dom before observing
        if (this.$refs.filterNav) {
          this.observed = this.$refs.filterNav;
          // check for sticky position
          this.observer = new IntersectionObserver(
            ([e]) => {
              this.sticky_active = e.intersectionRatio < 1;
            },
            { threshold: [1] }
          );
          // attach the observer
          this.observer.observe(this.observed);
        }
      },
      unobserveFilter() {
        if (this.observed) {
          this.observer.unobserve(this.observed);
        }
      }
    },
    computed: {
      currentCLR() {
        let vm = this;

        if (!vm.clrData.results)
          return;

        return vm.clrData?.results.find(item => {
          return item.sub_round_slug == vm.params?.sub_round_slug;
        });
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
      this.getUrlParams();
      this.loadTab();
      window.addEventListener('scroll', this.scrollBottom, {passive: true});
    },
    beforeDestroy() {
      window.removeEventListener('scroll', this.scrollBottom);
      window.removeEventListener('cartDataUpdated', this.updateCartData);
      this.observer.unobserve(vm.$refs.filterNav);
    },
    mounted() {
      let vm = this;

      vm.fetchClrGrants();
      // vm.fetchGrants(vm.params.page);
      vm.getTag(undefined, '');
      // delay work till next tick to make sure els are present
      vm.$nextTick(()=>{
        // check for sticky position
        vm.observeFilter();
        // watch for cartUpdates
        window.addEventListener('cartDataUpdated', this.updateCartData);
        // hide cart dropdown on show of any other
        vm.$root.$on('bv::dropdown::show', bvEvent => {
          $('.navCart.dropdown').dropdown('hide');
        });
      });
    }
  });
}
