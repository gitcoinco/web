if (document.getElementById('gc-search')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-search',
    data: {
      term: '',
      results: [],
      page: 0,
      total: 0,
      perPage: 100,
      searchTerm: '',
      isLoading: false,
      isTypeSearchLoading: false,
      tabPageCount: {
        Profile: 0,
        Bounty: 0,
        Grant: 0,
        Kudos: 0,
        Quest: 0,
        Page: 0
      },
      isDirty: false,
      currentTab: 0,
      source_types: [
        'All',
        'Profile',
        'Bounty',
        'Grant',
        'Kudos',
        'Quest',
        'Page'
      ],
      labels: {
        'All': 'All',
        'Profile': 'Profiles',
        'Bounty': 'Bounties',
        'Grant': 'Grants',
        'Kudos': 'Kudos',
        'Quest': 'Quests',
        'Page': 'Pages'
      },
      fetchController: new AbortController()
    },
    mounted() {
      this.search();
    },
    created() {
      this.search();
    },
    computed: {
      sourceType() {
        return this.source_types[this.currentTab];
      },
      currentTotal() {
        return this.totals[this.sourceType];
      },
      currentPage() {
        const page = this.currentTab > 0 ? this.tabPageCount[this.sourceType] : this.page;

        return page;
      },
      hasMoreResults() {
        return this.page !== false && this.total && this.page * this.perPage < this.total;
      }
    },
    methods: {
      checkForMoreResults: function(source_type) {
        console.log({ source_type });
      },
      init: function() {
        setTimeout(() => {
          $('.has-search input[type=text]').focus();
        }, 100);
      },
      loadMoreResults: function() {
        if (this.sourceType === 'All') {
          this.search();
          return;
        }
        this.search_type(this.sourceType);
      },
      clear: function() {
        this.results = [];
        this.page = 0;
        this.total = 0;
      },
      dirty: async function(e) {
        // only abort if we're not dirty
        if (!this.isDirty) {
          // mark as dirty
          this.isDirty = true;
          // clear state
          this.clear();
          // abort previous fetch request
          this.fetchController.abort();
          // setup a new AbortController
          this.fetchController = new AbortController();
        }
      },
      change_tab: function(index, source_type) {
        const vm = this;

        vm.currentTab = index;

        if (index > 0) {
          vm.tabPageCount[source_type] = 0;
          vm.search_type(source_type);
        } else {
          vm.page = 0;
          vm.search();
        }
      },
      search_type: async function(type) {
        const vm = this;
        // use signal to kill fetch req
        const { signal } = vm.fetchController;


        if (vm.isTypeSearchLoading) {
          return;
        }

        if (vm.term.length >= 3) {
          vm.isTypeSearchLoading = true;
          fetch(
            `/api/v0.1/search/?term=${vm.term}&page=${vm.tabPageCount[type]}&type=${type}`,
            {
              method: 'GET',
              signal: signal
            }
          ).then((res) => {
            res.json().then((response) => {
              if (vm.tabPageCount[type] === 0) {
                vm.results = response.results;
              } else {
                vm.results.push(...response.results);
              }
              vm.isTypeSearchLoading = false;
              vm.tabPageCount[type] = response.page;
            });
          }).catch(() => {
            if (document.current_search == thisDate) {
              // clear the results
              vm.clear();
              // clear loading states
              vm.isTypeSearchLoading = false;
            }
          });
        }

      },
      search: async function(e) {
        const vm = this;
        // use Date to enforce
        const thisDate = new Date();
        // use signal to kill fetch req
        const { signal } = vm.fetchController;

        // clear fetch state
        vm.isDirty = false;

        // prevent 2x search at once (ignores second request with same intel)
        if (vm.isLoading) {
          return;
        }

        // get results from the api and group
        if (vm.term.length >= 3) {
          // mark as reloading
          vm.isLoading = true;
          // mark thisDate against component to check for race conditions
          document.current_search = thisDate;
          // fetch the response from the api
          fetch(
            `/api/v0.1/search/?term=${vm.term}&page=${vm.page}`,
            {
              method: 'GET',
              signal: signal
            }
          ).then((res) => {
            if (document.current_search == thisDate) {
              res.json().then((response) => {
                if (vm.page === 0) {
                  vm.results = response.results;
                } else {
                  vm.results.push(...response.results);
                }
                vm.searchTerm = vm.term;
                vm.totals = response.totals;
                vm.page = response.page;
                vm.perPage = response.perPage;
                // clear loading states
                vm.isLoading = false;
              });
            }
          }).catch(() => {
            if (document.current_search == thisDate) {
              // clear the results
              vm.clear();
              // clear loading states
              vm.isLoading = false;
            }
          });
        } else {
          // clear the results
          vm.clear();
          // clear loading states
          vm.isLoading = false;
        }
      }
    }
  });
}
document.current_search = new Date();

$(document).on('click', '.gc-search .dropdown-menu', function(event) {
  event.stopPropagation();
});
