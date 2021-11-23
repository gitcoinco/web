let grantsNumPages = '';
let grantsHasNext = false;
let numGrants = '';


$(document).ready(() => {

  localStorage.setItem('last_grants_title', $('title').text().split('|')[0]);

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

});

if (document.getElementById('grants-showcase')) {
  const baseParams = {
    page: 1,
    limit: 12,
    me: false,
    sort_option: 'weighted_shuffle',
    collection_id: false,
    network: 'mainnet',
    state: 'active',
    profile: false,
    sub_round_slug: false,
    collections_page: 1,
    grant_regions: [],
    grant_types: [],
    grant_tags: [],
    tenants: [],
    idle: false,
    featured: true
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
      network: document.network,
      keyword: document.keyword,
      current_type: document.current_type,
      idle_grants: document.idle_grants,
      following: document.following,
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
      collection_title: document.collection_title,
      collection_description: document.collection_description,
      collection_owner: document.collection_owner,
      collection_owner_url: document.collection_owner_url,
      collection_owner_avatar: document.collection_owner_avatar,
      collection_grant_ids: document.collection_grant_ids,
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
      sticky_active: false,
      fetchedPages: [],
      handle: document.contxt.github_handle,
      editingCollection: false,
      createCollectionRedirect: false,
      activeTimeout: null,
      scrollTriggered: false,
      previouslyLoadedGrants: {},
      selectOptions: [
        {group: 'Discover', label: null},
        {label: 'Weighted Shuffle', value: 'weighted_shuffle'},
        {label: 'Trending', value: '-metadata__upcoming'},
        {label: 'Undiscovered Gems', value: '-metadata__gem'},
        {label: 'Recently Updated', value: '-last_update'},
        {label: 'Newest', value: '-created_on'},
        {label: 'Oldest', value: 'created_on'},
        {label: 'A to Z', value: 'title'},
        {label: 'Z to A', value: '-title'},
        {group: 'Current Round', label: null},
        {label: 'Most Relevant', value: ''},
        {label: 'Highest Amount Raised', value: '-amount_received_in_round'},
        {label: 'Highest Contributor Count', value: '-positive_round_contributor_count'},
        {group: 'All-Time', label: null},
        {label: 'Highest Amount Raised', value: '-amount_received'},
        {label: 'Highest Contributor Count', value: '-contributor_count'}
      ],
      adminOptions: [
        {group: 'Misc', label: null},
        {label: 'ADMIN: Risk Score', value: '-weighted_risk_score'},
        {label: 'ADMIN: Sybil Score', value: '-sybil_score'}
      ]
    },
    methods: {
      toggleStyle: function(style) {

        if (!style) {
          return;
        }

        if (style.inline_css) {
          $('.page-styles').last().text(style.inline_css);
        } else {
          $('.page-styles').last().text('');
        }
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

        vm.params = Object.assign({}, baseParams);
        vm.fetchedPages = [];
        vm.fetchGrants();

      },
      changeQuery: function(query) {
        let vm = this;

        vm.fetchedPages = [];
        vm.$set(vm, 'params', {...vm.params, ...query});

        if (vm.tabSelected === 'grants') {
          vm.fetchGrants();
        } else {
          vm.updateUrlParams();
        }
      },
      delayedChangeQuery: function() {
        if (this.params.keyword === '' && this.params.sort_option !== 'weighted_shuffle') {
          this.params.sort_option = 'weighted_shuffle';
        }

        if (this.activeTimeout) {
          window.clearTimeout(this.activeTimeout);
        }
        this.activeTimeout = setTimeout(() => {
          this.changeQuery({page: 1});
          this.activeTimeout = null;
        }, 500);
      },
      filterCollection: async function(collectionId) {
        let vm = this;

        // clear previous state
        vm.grants = [];
        vm.fetchedPages = [];
        vm.collection_id = '';
        vm.collection_title = '';
        vm.collection_description = '';
        vm.collection_owner = '';
        vm.collection_owner_avatar = '';

        // reset the params and set collection_id
        vm.params = Object.assign({}, baseParams);
        vm.$set(vm, 'params', {...vm.params, ...{page: 1, collection_id: collection_id }});

        // fetch the collections details
        const collectionDetailsURL = `/grants/v1/api/collections/${collection_id}`;
        const collection = await fetchData(collectionDetailsURL, 'GET');

        // update the stored state
        vm.$set(vm, 'collection_id', collection_id);
        vm.$set(vm, 'collection_title', collection.title);
        vm.$set(vm, 'collection_description', collection.description);
        vm.$set(vm, 'collection_owner', collection.owner.handle);
        vm.$set(vm, 'collection_owner_url', collection.owner.url);
        vm.$set(vm, 'collection_owner_avatar', collection.owner.avatar_url);
        vm.$set(vm, 'collection_grant_ids', JSON.parse(collection.grant_ids));

        // move to the grants tab
        vm.tabIndex = 0;

        // update the grants
        vm.fetchGrants();

        // move to the top
        window.scrollTo(0, 0);
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
              vm.params[param_key] = [];
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
      updateUrlParams: function(replaceHistory) {
        let vm = this;

        // ignore idle/featured if collection_id is set - always show everything
        if (vm.params.collection_id) {
          vm.params.idle = true;
          vm.params.featured = false;
        }

        vm.searchParams = new URLSearchParams(vm.params);

        if (replaceHistory) {
          window.history.replaceState({}, '', `${location.pathname}?${vm.searchParams}`);
        } else {
          window.history.pushState({}, '', `${location.pathname}?${vm.searchParams}`);
        }
      },
      unshiftGrants: async function(page) {
        let vm = this;

        await vm.updateUrlParams();

        vm.searchParams.set('page', page);
        vm.fetchedPages.push(page);

        const getGrants = await (await fetch(`/grants/cards_info?${vm.searchParams.toString()}`)).json();

        getGrants.grants.forEach(function(item) {
          vm.grants.unshift(item);
        });


      },
      fetchGrants: async function(page, append_mode, replaceHistory) {
        let vm = this;

        if (page) {
          vm.params.page = page;
        }

        await vm.updateUrlParams(replaceHistory);

        if (vm.lock)
          return;

        vm.scrollTriggered = append_mode;
        vm.lock = true;
        const requestGrants = await fetch(`/grants/cards_info?${vm.searchParams.toString()}`);

        if (!requestGrants.ok) {
          vm.lock = false;
          vm.scrollTriggered = false;
          vm.grantsHasNext = true;
          return;
        }
        const getGrants = await requestGrants.json();

        if (!append_mode) {
          vm.grants = [];
          vm.prevouslyLoadedGrants = {};
        }

        getGrants.grants.forEach(function(item) {
          if (!vm.prevouslyLoadedGrants[item.id]) {
            vm.grants.push(item);
            vm.previouslyLoadedGrants[item.id] = item;
          }
        });

        vm.fetchedPages = [ ...vm.fetchedPages, Number(vm.params.page) ];

        vm.credentials = getGrants.credentials;
        vm.contributions = getGrants.contributions;

        vm.grant_types = getGrants.grant_types.sort((a, b) => {
          a = a.label.toLocaleLowerCase();
          b = b.label.toLocaleLowerCase();

          return a > b ? 1 : a == b ? 0 : -1;
        });

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
        vm.scrollTriggered = false;

        return vm.grants;
      },
      tabChange: function(input) {
        let vm = this;

        vm.tabSelected = vm.$refs.grantstabs.tabs[input].id;
        vm.fetchedPages = [];
        vm.$set(vm, 'params', {...vm.params, ...{tab: vm.tabSelected}});

        vm.unobserveFilter();
        vm.params.profile = false;

        if (vm.tabSelected === 'collections') {
          this.fetchCollections();
        } else {
          this.fetchGrants(1);
          setTimeout(() => vm.observeFilter());
        }
      },
      loadTab: function(replaceHistory) {
        let vm = this;
        let loadParams = new URLSearchParams(document.location.search);
        const tabStrings = [
          {'index': 0, 'string': 'grants'},
          {'index': 1, 'string': 'collections'}
        ];
        // tabs are 0 key indexed by b-tabs

        if (loadParams.has('tab')) {
          vm.tabSelected = loadParams.get('tab');
          vm.tabIndex = tabStrings.filter(tab => tab.string === vm.tabSelected)[0].index;
        }
        // *NOTE: collections are paginated by using the returned .next url (stored as collectionsPage)
        if (vm.tabSelected === 'collections') {
          vm.params.page = 1;
          vm.collections = [];
          // move to the top on tabChange
          vm.collectionsPage = false;
          this.fetchCollections(false, replaceHistory);
        } else {
          this.fetchGrants(undefined, undefined, replaceHistory);
        }
      },
      fetchCollections: async function(append_mode, replaceHistory) {
        let vm = this;

        if (vm.loadingCollections)
          return;

        vm.loadingCollections = true;

        await vm.updateUrlParams(replaceHistory);

        const profile = (vm.params.profile ? 'profile=' + vm.params.profile : '');
        const featured = (vm.params.featured ? 'featured=' + vm.params.featured : '');

        let url = `/api/v0.1/grants_collections/?${profile}&${featured}`;

        if (vm.collectionsPage && append_mode) {
          url = vm.collectionsPage;
        }

        let getCollections = await fetch(url);
        let collectionsJson = await getCollections.json();

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
        const pageHeight = document.documentElement.scrollHeight - 1600;
        const bottomOfPage = visible + scrollY >= pageHeight;
        const topOfPage = visible + scrollY <= pageHeight;


        if (bottomOfPage || pageHeight < visible) {
          if (vm.params.tab === 'collections' && vm.collectionsPage) {
            await vm.fetchCollections(true);
          } else if (vm.grantsHasNext && !vm.pageIsFetched(vm.params.page + 1)) {
            await vm.fetchGrants(vm.params.page, true, true);
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
      tagSearch: function(search, loading) {
        const vm = this;

        // if (search.length < 3) {
        //   return;
        // }
        loading(true);
        vm.getTag(loading, search);

      },
      getTag: async function(loading, search) {
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
              vm.$set(vm, 'tagsOptions', json.sort((a, b) => {
                a = a.name.toLocaleLowerCase();
                b = b.name.toLocaleLowerCase();

                return a > b ? 1 : a == b ? 0 : -1;
              }));

              resolve();
            });
            if (loading) {
              loading(false);
            }
          });
        });
      },
      addCollectionToCart: async function(collection_id) {
        const collectionDetailsURL = `/grants/v1/api/collections/${collection_id}`;
        const collection = await fetchData(collectionDetailsURL, 'GET');

        (collection.grants || []).forEach((grant) => {
          CartData.addToCart(grant);
        });
      },
      updateCartData: function(e) {
        const grants_in_cart = (e && e.detail && e.detail.list && e.detail.list) || [];
        const grant_ids_in_cart = grants_in_cart.map((grant) => grant.grant_id);

        this.cart_data_count = grants_in_cart.length;
        this.grants.forEach((grant) => {
          this.$set(grant, 'isInCart', (grant_ids_in_cart.indexOf(String(grant.id)) !== -1));
        });
      },
      scrollBottom: async function() {
        this.bottom = await this.scrollEnd();
      },
      closeDropdown: function(ref) {
        // Close the menu and (by passing true) return focus to the toggle button
        this.$refs[ref].hide(true);
      },
      observeFilter: function() {
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
      unobserveFilter: function() {
        if (this.observed) {
          this.observer.unobserve(this.observed);
        }
      },
      watchHistory: function(event) {
        this.getUrlParams();
        // set tab selected
        this.$set(this, 'tabSelected', this.params.tab);
        // load the correct tab
        this.loadTab(true);
      },
      pageIsFetched: function(page) {
        let vm = this;

        return vm.fetchedPages.includes(page);

      },
      showFilter: function() {
        let vm = this;
        let show_filter = false;

        const keys = [
          'limit',
          'me',
          'sort_option',
          'network',
          'state',
          'profile',
          'sub_round_slug',
          'collections_page',
          'grant_regions',
          'grant_types',
          'grant_tags',
          'tenants',
          'idle'
        ];

        keys.forEach(key => {
          if (vm.params[key].toString() != baseParams[key].toString()) {
            show_filter = true;
          }
        });

        return show_filter;
      },
      openCreateCollectionModal: function(doRedirect = false) {
        // set the redirect ref on <create-collection-modal>
        this.createCollectionRedirect = doRedirect;
        // show the createCollection modal
        this.$refs.createNewCollection.show();
      },
      shareCollection: function() {
        _alert('Collections URL copied to clipboard', 'success', 3000);
        const share_url = `${location.host}/grants/explorer?collection_id=${this.params.collection_id}`;

        copyToClipboard(share_url);
      },
      tweetCollection: function() {
        const share_url = `${location.host}/grants/explorer?collection_id=${this.params.collection_id}`;
        const tweetUrl = `https://twitter.com/intent/tweet?text=Check out this Grant Collection on @gitcoin ${share_url}`;

        window.open(tweetUrl, '_blank');
      },
      editCollection: function() {
        this.$set(this, 'editingCollection', true);
      },
      saveEditCollection: async function() {
        // pick up csrf token from dom
        const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        // wrap the changes to pass to the endpoint
        const body = {
          collection: this.params.collection_id,
          collectionTitle: this.collection_title,
          collectionDescription: this.collection_description,
          grants: this.collection_grant_ids,
          grantsComplete: true
        };

        // attempt to post the update to the collections api
        try {
          // attempt to fetch the data
          await fetchData('/grants/v1/api/collections/edit', 'POST', body, {'X-CSRFToken': csrfmiddlewaretoken});
          // toast the success
          _alert('Congratulations, your collection was updated successfully!', 'success');
        } finally {
          // find the collection in the document.collections obj
          const collection = document.collections.find((collection) => this.params.collection_id == collection.id);

          // update the title against the collection
          if (collection) {
            collection.title = body.collectionTitle;
          }
          // finish editing
          this.$set(this, 'editingCollection', false);
          // update the grant list by fetching again
          this.fetchedPages = [];
          this.fetchGrants();
        }
      },
      deleteCollection: function() {
        // deleteCollection exists as a component with selected_collection passed in as a prop
        this.$refs.deleteCollection.show();
      }
    },
    computed: {
      lowestPage() {
        let vm = this;

        return Math.min(...vm.fetchedPages);
      },
      grantsHasPrev() {
        let vm = this;

        return isFinite(vm.lowestPage) && vm.lowestPage > 1;
      },
      currentCLR() {
        let vm = this;

        if (!vm.clrData.results)
          return;

        const currentCLR = vm.clrData?.results.find(item => {
          return item.sub_round_slug == vm.params?.sub_round_slug;
        });

        function getMDT(date) {
          if (!date)
            return;
          return moment(date).tz('America/Denver').format('MMMM D (hA) z');
        }

        function getRoundStatus(start_date, end_date, claim_start_date, claim_end_date) {
          now = moment().tz('America/Denver');
          start_date = moment(start_date).tz('America/Denver');
          end_date = moment(end_date).tz('America/Denver');

          if (claim_start_date && claim_end_date) {
            claim_start_date = moment(claim_start_date).tz('America/Denver');
            claim_end_date = moment(claim_end_date).tz('America/Denver');
          }

          if (now.isBefore(start_date)) {
            // round is yet to start
            return 'proposed';
          } else if (now.isBetween(start_date, end_date)) {
            // round is currently live
            return 'live';
          } else if (
            claim_start_date && claim_end_date &&
            now.isBetween(claim_start_date, claim_end_date)
          ) {
            // claim period is live
            return 'claim';
          }
          // round has ended
          return 'ended';

        }

        if (currentCLR) {
          const formatted_dates = {
            start_date: getMDT(currentCLR?.start_date),
            end_date: getMDT(currentCLR?.end_date),
            claim_start_date: getMDT(currentCLR?.claim_start_date),
            claim_end_date: getMDT(currentCLR?.claim_end_date),
            status: getRoundStatus(
              currentCLR?.start_date,
              currentCLR?.end_date,
              currentCLR?.claim_start_date,
              currentCLR?.claim_end_date
            )
          };

          currentCLR.formatted_dates = formatted_dates;
        }

        return currentCLR;

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
      },
      showLoading() {
        return this.lock && !this.scrollTriggered;
      }
    },
    beforeMount() {
      this.getUrlParams();
      this.loadTab();
      window.addEventListener('scroll', this.scrollBottom, {passive: true});
      // watch for history changes
      window.addEventListener('popstate', this.watchHistory);
    },
    beforeDestroy() {
      window.removeEventListener('scroll', this.scrollBottom);
      window.removeEventListener('cartDataUpdated', this.updateCartData);
      window.removeEventListener('popstate', this.watchHistory);
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
