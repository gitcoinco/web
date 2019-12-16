let bounties = [];
let bountiesPage = 1;
let BountiesLimit = 10;
let BountiesOffset = 0;
let bountiesNumPages = '';
let bountiesHasNext = false;
let numBounties = '';
// let funderBounties = [];
let paramsDefault = {
  order_by: '-web3_created',
  idx_status: '',
  experience_level: [],
  project_type: [],
  applicants: '',
  bounty_filter: '',
  bounty_categories: [],
  moderation_filter: '',
  permission_type: [],
  project_length: [],
  bounty_type: [],
  network: ['mainnet']
}

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
        console.log(p, typeof vm.params[p[0]])
        vm.params[p[0]] = typeof vm.params[p[0]] === 'object' ? p[1].split(',') : p[1];
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
      vm.params = paramsDefault;
    },
    // check() {
    //   let vm = this;

    //   vm.params['experience_level'] =  vm.experienceSelected;
    // },
    closeModal() {
      this.$refs['user-modal'].closeModal();
    },
    popoverConfig(bounty) {
      console.log(bounty)
      // Both title and content specified as a function in this example
      // and will be called the each time the popover is opened
      return `
        <div>
          <div class="popover-bounty__content">
            <div class="d-flex justify-content-between mb-2">
              <span class="status-${bounty.status}">
                <i class="g-icon g-icon__dot-circle"></i>
                ${bounty.status === 'open' ? 'Ready to work' :
                  bounty.status === 'started' ? 'Work Started' :
                  bounty.status === 'submitted' ? 'Work Submitted' :
                  bounty.status === 'done' ? 'Work Done' :
                  bounty.status === 'cancelled' ? 'Cancelled' :
                  bounty.status === 'expired' ? 'Expired' : ''}
              </span>
              <span><img src="${bounty.avatar_url}" alt="${bounty.github_org_name}" class="rounded-circle ${bounty.github_org_name}" height="14"> ${bounty.github_org_name}</span>
            </div>
            <div class="font-subheader title text-truncate">${bounty.title}</div>
            <div class="mt-2 keyword-group">
              ${bounty.keywords.split(',').map((keyword) => `<span class="tag keyword">${keyword}</span>`).join(' ')}
            </div>
            <div class="mt-2">
              ${bounty.expires_date ? `<i class="far fa-clock expired-icon"></i> ${moment.utc(bounty.expires_date).fromNow()}` : '' }
            </div>
          </div>
          ${ bounty.latest_activity ? `
            <div class="popover-bounty__footer">
              <span class="title">Latest Activity</span>
                <div class="d-flex justify-content-between">
                  <span>${bounty.latest_activity.activity_type.replace(/_/i, ' ')} by <b>${bounty.latest_activity.profile.handle}</b></span>
                  <span>${moment.utc(bounty.latest_activity.created).fromNow()}</span>
                </div>
            </div>`
          : ''}

        </div>`

    }
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
      showExtraParams: false,
      params: {
        order_by: '-web3_created',
        idx_status: '',
        experience_level: [],
        project_type: [],
        applicants: '',
        bounty_filter: '',
        bounty_categories: [],
        moderation_filter: '',
        permission_type: [],
        project_length: [],
        bounty_type: [],
        network: ['mainnet']
      },
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

          // return this.params.experience_level = this.experienceSelected

        // return this.experienceSelected.map(item => this.params.experience_level = item);
        // this.check()
      },



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
    updated() {
      $(function () {
          $('[data-toggle="popover"]').popover()
      })
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

Vue.filter('stringFixer', (str) => {
  return str.replace(/_/i, ' ');
});
