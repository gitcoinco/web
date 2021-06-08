let bounties = [];
let featuredBounties = [];
let bountiesPage = 1;
let BountiesLimit = 10;
let BountiesOffset = 0;
let bountiesNumPages = '';
let bountiesHasNext = false;
let numBounties = '';
// let funderBounties = [];
let paramsDefault = {
  order_by: '-web3_created',
  idx_status: 'open',
  experience_level: [],
  project_type: [],
  applicants: '',
  bounty_filter: '',
  bounty_categories: [],
  moderation_filter: '',
  permission_type: [],
  project_length: [],
  bounty_type: [],
  network: [document.web3network || 'mainnet'],
  keywords: []
};

Vue.filter('stringFixer', (str) => {
  return str.replace(/_/i, ' ');
});

Vue.mixin({
  methods: {
    clearParams() {
      let vm = this;

      vm.params = paramsDefault;
    },
    fetchBounties: function(newPage, featured) {
      let vm = this;

      vm.isLoading = true;
      vm.noResults = false;
      vm.params.limit = vm.BountiesLimit;
      if (newPage || newPage === 0) {
        vm.BountiesOffset = newPage;
      }
      vm.params.offset = vm.BountiesOffset;
      if (vm.searchTerm) {
        vm.params.search = vm.searchTerm;
      } else {
        delete vm.params['search'];
      }

      let searchParams = new URLSearchParams(vm.params);

      // window.history.replaceState({}, '', `${location.pathname}?${searchParams}`);

      let apiUrlBounties = `/api/v0.1/bounties/slim/?${searchParams.toString()}`;

      if (featured) {
        apiUrlBounties = `/api/v0.1/bounties/slim/?${searchParams.toString()}&is_featured=True`;
      }
      // vm.bounties = [];
      const getBounties = fetchData (apiUrlBounties, 'GET');

      $.when(getBounties).then(function(response) {

        response.forEach(function(item) {
          if (featured) {
            vm.featuredBounties.push(item);
          } else {
            vm.bounties.push(item);
          }
        });

        if (featured) {
          return vm.featuredBounties;
        }
        vm.numBounties = response.length;
        if (vm.numBounties < vm.BountiesLimit) {
          vm.bountiesHasNext = false;
        } else {
          vm.bountiesHasNext = true;
        }
        if (vm.bountiesHasNext) {
          vm.BountiesOffset = vm.BountiesOffset + vm.BountiesLimit;

        } else {
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
    searchBounties: function() {
      let vm = this;

      vm.bounties = [];
      vm.featuredBounties = [];
      vm.fetchBounties(0);
      vm.fetchBounties(0, true);
    },
    getUrlParams: function() {
      let vm = this;

      const url = new URL(location.href);
      const params = new URLSearchParams(url.search);

      for (let p of params) {
        if (typeof vm.params[p[0]] === 'object') {
          if (p[1].length > 0) {
            vm.params[p[0]] = p[1].split(',');
          } else {
            vm.$delete(vm.params[p[0]]);
          }
        } else {
          vm.params[p[0]] = p[1];
        }
      }
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
    closeModal() {
      this.$refs['user-modal'].closeModal();
    },
    removeFilter(prop, index, obj) {
      let vm = this;

      if (obj) {
        vm.$delete(vm.params[prop], index);
      } else {
        vm.$set(vm.params, prop, '');
      }
    },
    popoverConfig(bounty) {
      moment.locale('en');
      return `
        <div>
          <div class="popover-bounty__content">
            <div class="d-flex justify-content-between mb-2">
              <span class="status-${bounty.status}"> <i class="g-icon g-icon__dot-circle"></i> ${bounty.status === 'open' ? 'Ready to work' : bounty.status === 'started' ? 'Work Started' : bounty.status === 'submitted' ? 'Work Submitted' : bounty.status === 'done' ? 'Work Done' : bounty.status === 'cancelled' ? 'Cancelled' : bounty.status === 'expired' ? 'Expired' : ''}</span>
              <span><img src="${bounty.avatar_url}" alt="${bounty.github_org_name}" class="rounded-circle ${bounty.github_org_name}" height="14"> ${bounty.github_org_name}</span>
            </div>
            <div class="font-subheader title text-truncate">${bounty.title}</div>
            <div class="mt-2 keyword-group">
              ${bounty.keywords.split(',').map((keyword) => `<span class="tag keyword">${keyword}</span>`).join(' ')}
            </div>
            <div class="mt-2">
              ${moment(bounty.expires_date).diff(moment(), 'years') < 1 ? `<i class="far fa-clock expired-icon"></i> ${moment(bounty.expires_date) < moment() ? 'Expired' : 'Expires'}  ${moment.utc(bounty.expires_date).fromNow()}` : 'Never expires' }
            </div>
          </div>
          ${ bounty.latest_activity ? `
            <div class="popover-bounty__footer">
              <span class="title">Latest Activity</span>
                <div class="d-flex justify-content-between">
                  <span>${bounty.latest_activity.activity_type.replace(/_/i, ' ')} by <b>${bounty.latest_activity.profile.handle}</b></span>
                  <span>${moment.utc(bounty.latest_activity.created).fromNow()}</span>
                </div>
            </div>` : ''}

        </div>`;

    }
  }
});

Vue.component('bounty-explorer', Vue.extend({
  delimiters: [ '[[', ']]' ],
  props: ['tribe'],
  data: function() {
    return {
      bounties,
      featuredBounties,
      bountiesPage,
      BountiesLimit,
      BountiesOffset,
      bountiesNumPages,
      bountiesHasNext,
      numBounties,
      media_url,
      orderByOptions: [
        { name: 'Created: Recent', value: '-web3_created'},
        { name: 'Created: Oldest', value: 'web3_created' },
        { name: 'Value: Highest', value: '-_val_usd_db'},
        { name: 'Value: Lowest', value: '_val_usd_db'}
      ],
      searchTerm: null,
      bottom: false,
      experienceSelected: [],
      showExtraParams: false,
      params: paramsDefault,
      showFilters: true,
      noResults: false,
      isLoading: true
    };
  },
  mounted() {
    let vm = this;

    vm.bounties = [];
    vm.featuredBounties = [];
    if (this.tribe && this.tribe.handle) {
      this.params.org = this.tribe.handle;
    }
    this.fetchBounties();
    this.fetchBounties(0, true);
    this.$watch('params', function(newVal, oldVal) {
      if (this.tribe && this.tribe.handle) {
        this.params.org = this.tribe.handle;
      }
      this.searchBounties();
    }, {
      deep: true
    });
  },
  updated() {
    $(function() {
      $('[data-toggle="popover"]').popover();
    }),
    scrollSlider($('#featured-card-container'), 288);
    if (this.tribe && this.tribe.handle) {
      // this.bounties = this.tribe.active_bounties;
      this.params.org = this.tribe.handle;
    }
  },
  beforeMount() {
    if (this.isMobile) {
      this.showFilters = false;
    }
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    }, false);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    });
  }
}));

if (document.getElementById('gc-explorer')) {
  var appExplorer = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-explorer',
    data: {
      bounties,
      featuredBounties,
      bountiesPage,
      BountiesLimit,
      BountiesOffset,
      bountiesNumPages,
      bountiesHasNext,
      numBounties,
      media_url,
      searchTerm: null,
      bottom: false,
      experienceSelected: [],
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
        network: ['mainnet'],
        keywords: []
      },
      showFilters: true,
      noResults: false,
      isLoading: true
    },
    mounted() {
      this.getUrlParams();
      this.fetchBounties();
      this.fetchBounties(0, true);
      this.$watch('params', function(newVal, oldVal) {
        this.searchBounties();
      }, {
        deep: true
      });
    },
    updated() {
      $(function() {
        $('[data-toggle="popover"]').popover();
      }),
      scrollSlider($('#featured-card-container'), 288);

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

function scrollSlider(element, cardSize) {
  const arrowLeft = $('#arrowLeft');
  const arrowRight = $('#arrowRight');

  arrowLeft.on('click', function() {
    element[0].scrollBy({left: -cardSize, behavior: 'smooth'});
  });
  arrowRight.on('click', function() {
    element[0].scrollBy({left: cardSize, behavior: 'smooth'});
  });

  element.on('scroll mouseenter', function() {
    if (this.clientWidth === (this.scrollWidth - this.scrollLeft)) {
      arrowRight.hide();
    } else {
      arrowRight.show();
    }

    if (this.scrollLeft < 10) {
      arrowLeft.hide();
    } else {
      arrowLeft.show();
    }
  });
}

