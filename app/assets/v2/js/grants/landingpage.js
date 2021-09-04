const grantsNumPages = '';
const grantsHasNext = false;
const numGrants = '';


if (document.getElementById('grants-showcase')) {

  let sort = getParam('sort');

  if (!sort) {
    sort = 'weighted_shuffle';
  }
  var appGrants = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#grants-showcase',
    data: {
      activePage: document.activePage,
      grants: [],
      grant: {},
      page: 1,
      collectionsPage: null,
      limit: 6,
      show_active_clrs: window.localStorage.getItem('show_active_clrs') != 'false',
      sort: sort,
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
      grantsNumPages,
      grantsHasNext,
      numGrants,
      mainBanner: document.current_style,
      visibleModal: false,
      bannerCollapsed: false,
      loadingCollections: false,
    },
    methods: {
      fetchCollections: async function(append_mode) {
        let vm = this;

        if (vm.loadingCollections)
          return;

        vm.loadingCollections = true;

        // vm.updateUrlParams();

        let url = '/api/v0.1/grants_collections/?featured=true';

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
      toggleActiveCLRs() {
        this.show_active_clrs = !this.show_active_clrs;
        window.localStorage.setItem('show_active_clrs', this.show_active_clrs);
      },
      scrollEnd: async function(event) {
        const vm = this;

        const scrollY = window.scrollY;
        const visible = document.documentElement.clientHeight;
        const pageHeight = document.documentElement.scrollHeight - 500;
        const bottomOfPage = visible + scrollY >= pageHeight;

        if (bottomOfPage || pageHeight < visible) {

        }
      },
      showModal(modalName) {
        this.visibleModal = modalName;
      },
      hideModal() {
        this.visibleModal = 'none';
      },
      toggleBannerCollapse() {
        this.bannerCollapsed = !this.bannerCollapsed;
        // record into ls
        localStorage.setItem('bannerCollapsed', this.bannerCollapsed);
      }
    },
    computed: {
      isLandingPage() {
        return (this.activePage == 'grants_landing');
      }
    },
    beforeMount() {
      this.fetchCollections();
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
      const vm = this;

      vm.bannerCollapsed = localStorage.getItem('bannerCollapsed') == 'true';
    }
  });
}

