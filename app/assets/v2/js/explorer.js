let bounties = [];
let bountiesPage = 1;
let BountiesLimit = 2;
let BountiesOffset = 0;
let bountiesNumPages = '';
let bountiesHasNext = false;
let numBounties = '';
// let funderBounties = [];

Vue.mixin({
  methods: {
    fetchBounties: function(newPage) {
      let vm = this;

      vm.isLoading = true;
      vm.noResults = false;
      // vm.params.network = 'rinkeby';
      // vm.params.page = vm.bountiesPage;
      vm.params.limit = vm.BountiesLimit;
      if (newPage || newPage === 0 ) {
        // vm.bountiesPage = newPage;
        vm.BountiesOffset = newPage;
      }
      vm.params.offset = vm.BountiesOffset;
      console.log(vm.params.limit, vm.params.offset)

      if (vm.searchTerm) {
        vm.params.search = vm.searchTerm;
      } else {
        delete vm.params['search'];
      }

      let searchParams = new URLSearchParams(vm.params);
      window.history.replaceState({}, '', `${location.pathname}?${searchParams}`);


      let apiUrlBounties = `/api/v0.1/bounties/slim/?${searchParams.toString()}`;

      var getBounties = fetchData (apiUrlBounties, 'GET');

      $.when(getBounties).then(function(response) {

        response.forEach(function(item) {
          vm.bounties.push(item);
        });

        // vm.bountiesNumPages = response.num_pages;
        vm.numBounties = response.length;
        if (vm.numBounties < vm.BountiesLimit) {
          vm.bountiesHasNext = false;
        } else {
          vm.bountiesHasNext = true;
        }
        // vm.bountiesHasNext = response.has_next;
        if (vm.bountiesHasNext) {
          vm.BountiesOffset = vm.BountiesOffset + vm.BountiesLimit;
        //   vm.bountiesPage = ++vm.bountiesPage;

        } else {
        //   vm.bountiesPage = 1;
          vm.BountiesOffset = 0;

        }

        if (vm.bounties.length) {
          vm.noResults = false;
        } else {
          vm.noResults = true;
        }
        vm.isLoading = false;
      });
    },
    getUrlParams: function() {
      let vm = this;

      const url = new URL(location.href);
      const params = new URLSearchParams(url.search);
      for (let p of params) {
        console.log(p)
        vm.params[p[0]] = p[1]
      }
    },
    searchBounties: function() {
      let vm = this;

      vm.bounties = [];
      vm.fetchBounties(0);
      console.log( 'here')

    },
    bottomVisible: function() {
      let vm = this;

      const scrollY = window.scrollY;
      const visible = document.documentElement.clientHeight;
      const pageHeight = document.documentElement.scrollHeight - 500;
      const bottomOfPage = visible + scrollY >= pageHeight;

      if (bottomOfPage || pageHeight < visible) {
        if (vm.bountiesHasNext) {
          vm.fetchBounties();
          vm.bountiesHasNext = false;
        }
      }
    },
    clearParams() {
      let vm = this;
      vm.params = {};
      vm.experienceSelected = []

    },
    // check() {
    //   let vm = this;

    //   vm.params['experience_level'] =  vm.experienceSelected;
    // },
    closeModal() {
      this.$refs['user-modal'].closeModal();
    },
  }
});

if (document.getElementById('gc-explorer')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-explorer',
    data: {
      bounties,
      bountiesPage,
      BountiesLimit,
      BountiesOffset,
      bountiesNumPages,
      bountiesHasNext,
      numBounties,
      media_url,
      searchTerm: null,
      bottom: false,
      experienceSelected:[],
      params: { },
      // experience_options: [
      //   {
      //     id: 1,
      //     name: 'beginner',
      //   },
      //   {
      //     id: 2,
      //     name: 'intermediate',
      //   },
      //   {
      //     id: 3,
      //     name: 'advanced',
      //   }
      // ],
      showFilters: true,
      noResults: false,
      isLoading: true
    },
    computed:{
      // flatSelected () {
      //   return this.params.experience_level.reduce((acc, cur) => [ ...acc, ...cur ], [])
      // }
      foos(){

          return this.params.experience_level = this.experienceSelected

        // return this.experienceSelected.map(item => this.params.experience_level = item);
        // this.check()
      }
    },
    mounted() {
      this.getUrlParams();
      this.fetchBounties();
      this.$watch('params', function(newVal, oldVal) {
        this.searchBounties();
      }, {
        deep: true
      });
    },
    created() {
      // this.fetchBounties();
    },
    beforeMount() {
      window.addEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      }, false);
    },
    beforeDestroy() {
      window.removeEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      });
    }
  });
}
