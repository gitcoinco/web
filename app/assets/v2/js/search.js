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
      }
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
      dirty: async function(e) {
        this.isDirty = true;
      },
      search: async function(e) {
        let vm = this;
        let thisDate = new Date();

        vm.isDirty = false;
        // prevent 2x search at once
        if (vm.isLoading) {
          return;
        }

        // clear state on new search term
        if (vm.term !== vm.searchTerm) {
          vm.results = {};
          vm.page = 0;
          vm.total = 0;
        }

        // get results from the api and group
        if (vm.term.length >= 4) {
          vm.isLoading = true;
          document.current_search = thisDate;

          const response = await fetchData(
            `/api/v0.1/search/?term=${vm.term}&page=${vm.page}`,
            'GET'
          );

          if (document.current_search == thisDate) {
            vm.results = groupBySource(response.results, vm.term !== vm.searchTerm ? {} : vm.results);
            vm.searchTerm = vm.term;
            vm.total = response.total;
            vm.page = response.page;
            vm.perPage = response.perPage;
          }
          vm.isLoading = false;
        } else {
          vm.results = {};
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
