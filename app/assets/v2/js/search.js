if (document.getElementById('gc-search')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-search',
    data: {
      term: '',
      results: [],
      currentTab: 0,
      source_types: [
        'Profile',
        'Bounty',
        'Grant',
        'Kudos',
        'Quest',
        'Page'
      ],
      labels: {
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
    methods: {
      search: async function() {
        let vm = this;

        if (vm.term.length > 3) {
          const response = await fetchData(
            `/api/v0.1/search/?term=${vm.term}`,
            'GET'
          );

          vm.results = groupBySource(response);
        } else {
          vm.results = {};
        }
      }
    }
  });
}

const groupBySource = results => {
  let grouped_result = {};

  results.map(result => {
    const source_type = result.source_type;

    grouped_result[source_type] ? grouped_result[source_type].push(result) : grouped_result[source_type] = [result];
  });
  return grouped_result;
};

$(document).on('click', '.gc-search .dropdown-menu', function (event) {
  event.stopPropagation();
});