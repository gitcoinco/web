/**
 * @notice Vue component for exploring grants
 */

let appGrants;

Vue.component('grants-explore-grants', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      grants: [],
      grant: {},
      page: 1,
      collectionsPage: 1,
      limit: 6,
      show_active_clrs: window.localStorage.getItem('show_active_clrs') != 'false',
      sort: 'weighted_shuffle',
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
      round_num: document.round_num,
      sub_round_slug: document.sub_round_slug,
      customer_name: document.customer_name,
      activeCollection: null,
      grantsNumPages: '',
      grantsHasNext: false,
      numGrants: ''
    };
  },

  methods: {
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
    updateURI: function() {
      let vm = this;
      const q = vm.getQueryParams();

      if (vm.round_num) {
        let uri = `/grants/clr/${vm.round_num}/`;

        if (vm.sub_round_slug && !vm.customer_name) {
          uri = `/grants/clr/${vm.round_num}/${vm.sub_round_slug}/`;
        }

        if (!vm.sub_round_slug && vm.customer_name) {
          uri = `/grants/clr/${vm.customer_name}/${vm.round_num}/`;
        }

        if (vm.sub_round_slug && vm.customer_name) {
          uri = `/grants/clr/${vm.customer_name}/${vm.round_num}/${vm.sub_round_slug}/`;
        }

        if (this.current_type === 'all') {
          window.history.pushState('', '', `${uri}?${q || ''}`);
        } else {
          window.history.pushState('', '', `${uri}?type=${this.current_type}&${q || ''}`);
        }
      } else {
        let uri = '/grants/';

        if (this.current_type === 'all') {
          window.history.pushState('', '', `${uri}?${q || ''}`);
        } else {
          window.history.pushState('', '', `${uri}${this.current_type}?${q || ''}`);
        }
      }

      if (this.current_type === 'activity') {
        const triggerTS = function() {
          const activeElement = $('.infinite-more-link');

          if (activeElement.length) {
            $('.infinite-more-link').click();
          } else {
            setTimeout(triggerTS, 1000);
          }
        };

        setTimeout(triggerTS, 1000);
      }
    },
    getQueryParams: function() {
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
      if (this.featured) {
        query_elements['featured'] = this.featured;
      }
      if (this.sort !== 'weighted_shuffle') {
        query_elements['sort'] = this.sort;
      }
      if (this.network !== 'mainnet') {
        query_elements['network'] = this.network;
      }
      if (this.current_type === 'collections') {
        if (this.collection_id) {
          query_elements['collection_id'] = this.collection_id;
        }
      }

      return $.param(query_elements);
    },
    filter_grants: function(filters, event) {
      if (event) {
        event.preventDefault();
      }
      let current_style;

      if (filters.type !== null && filters.type !== undefined) {
        if (!current_style) {
          current_style = document.all_type_styles[filters.type];
        }
        this.current_type = filters.type;
        if (this.current_type === 'collections') {
          this.collection_id = null;
        }
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
      if (filters.featured !== null && filters.featured !== undefined) {
        this.featured = filters.featured;
      }
      if (filters.network !== null && filters.network !== undefined) {
        this.network = filters.network;
      }

      if (filters.type === 'collections') {
        this.collectionsPage = 1;
      }
      this.page = 1;
      this.setCurrentType(this.current_type);
      this.fetchGrants(this.page);
      const regex_style = document.all_routing_policies.find(policy => {
        return new RegExp(policy.url_pattern).test(window.location.href);
      });

      toggleStyle(regex_style || current_style);

    },
    clearSingleCollection: function() {
      this.grants = [];
      this.collections = [];
      this.collection_id = null;
      this.activeCollection = null;
      this.page = 1;
      this.updateURI();
      this.fetchGrants();
    },
    showSingleCollection: function(collectionId) {
      this.collection_id = collectionId;
      this.collections = [];
      this.keyword = '';
      this.grants = [];
      this.page = 1;
      this.current_type = 'collections';
      this.updateURI();
      this.fetchGrants();
    },
    fetchGrants: async function(page, append_mode) {
      let vm = this;

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
        collections_page: this.collectionsPage,
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

      if (this.featured) {
        base_params['featured'] = this.featured;
      }

      if (this.current_type === 'collections' && this.collection_id) {
        base_params['collection_id'] = this.collection_id;
      }

      if (vm.round_num) {
        base_params['round_num'] = vm.round_num;
      }

      if (vm.sub_round_slug) {
        base_params['sub_round_slug'] = vm.sub_round_slug;
      }

      if (vm.customer_name) {
        base_params['customer_name'] = vm.customer_name;
      }

      const params = new URLSearchParams(base_params).toString();
      const getGrants = await fetchData(`/grants/cards_info?${params}`);
      
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
      } else {
        if (this.current_type === 'collections') {
          getGrants.collections.forEach(function(item) {
            vm.collections.push(item);
          });
        } else {
          vm.collections = getGrants.collections;
        }

        vm.credentials = getGrants.credentials;
        vm.grant_types = getGrants.grant_types;
        vm.contributions = getGrants.contributions;
      }

      vm.grantsNumPages = getGrants.num_pages;
      vm.grantsHasNext = getGrants.has_next;
      vm.numGrants = getGrants.count;

      if (vm.grantsHasNext) {
        vm.page = ++vm.page;
      } else {
        vm.page = 1;
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
          vm.fetchGrants(vm.page, true);
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
      const getGrants = await fetchData(`/grants/bulk_cart?${params}`);


      (getGrants.grants || []).forEach((grant) => {
        CartData.addToCart(grant, true);
      });

      showSideCart();
      _alert(`Congratulations, ${getGrants.grants.length} ${getGrants.grants.length > 1 ? 'grants were' : 'grants was'} added to your cart!`, 'success');
      this.cart_lock = false;
    },
    removeCollection: async function({collection, grant, event}) {
      const getGrants = await fetchData(`v1/api/collections/${collection.id}/grants/remove`, 'POST', {
        'grant': grant.id
      });

      this.grants = getGrants.grants;
    },

    handleError(err) {
      console.error(err); // eslint-disable-line no-console
      let message = 'There was an error';

      if (err.message)
        message = err.message;
      else if (err.msg)
        message = err.msg;
      else if (typeof err === 'string')
        message = err;

      _alert(message, 'error');
      this.submitted = false;
    }
  },

  computed: {
    isUserLogged() {
      if (document.contxt.github_handle) {
        return true;
      }
      return false;
    }
  },

  mounted() {
    // let vm = this;
    this.fetchGrants(this.page);

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

if (document.getElementById('gc-grants-explore-grants')) {

  appGrants = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-explore-grants'
  });
}
