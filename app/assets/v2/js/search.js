if (document.getElementById('gc-search')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-search',
    data: {
      term: '',
      results: {},
      page: 0,
      total: 0,
      perPage: 100,
      searchTerm: '',
      isLoading: false,
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
      hasMoreResults() {
        return this.page !== false && this.total && this.page * this.perPage < this.total;
      }
    },
    methods: {
      init: function() {
        setTimeout(() => {
          $('.has-search input[type=text]').focus();
        }, 100);
      },
      clear: function() {
        this.results = {};
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
        if (vm.term.length >= 4) {
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
                vm.results = groupBySource(response.results, vm.term !== vm.searchTerm ? {} : vm.results);
                vm.searchTerm = vm.term;
                vm.total = response.total;
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

const groupBySource = (results, prev_results) => {
  let grouped_result = prev_results || {};

  results.map(result => {
    const source_type = result.source_type;

    grouped_result['All'] ? grouped_result['All'].push(result) : grouped_result['All'] = [result];
    grouped_result[source_type] ? grouped_result[source_type].push(result) : grouped_result[source_type] = [result];
  });
  return grouped_result;
};

$(document).on('click', '.gc-search .dropdown-menu', function(event) {
  event.stopPropagation();
});
