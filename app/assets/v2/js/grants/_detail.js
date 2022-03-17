
Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);
Quill.register('modules/ImageExtend', ImageExtend);


Vue.mixin({
  methods: {
    formatDonationAmounts(grant) {
      const amountReceived = Vue.filter('round')(grant.amount_received || 0);
      const amountRecievedInRound = Vue.filter('round')(grant.amount_received_in_round || 0);

      grant.amount_received = Vue.filter('formatNumber')(amountReceived);
      grant.amount_received_in_round = Vue.filter('formatNumber')(amountRecievedInRound);

      return grant;
    },
    fetchGrantDetails: function(id) {
      const vm = this;

      vm.loading = true;
      if (!id) {
        id = grantDetails.grant_id;
      }

      const url = `/grants/v1/api/grant/${id}/`;

      return new Promise(resolve => {

        fetch(url).then(function(res) {
          return res.json();
        }).then(function(json) {
          vm.grant = vm.formatDonationAmounts(json.grants);
          vm.loading = false;

          // pick up the curve from the grants model
          const clr_curve = vm.grant.clr_prediction_curve;

          // check if this grant has reached the cap for its respective clrs
          vm.grant.__has_reached_cap = clr_curve && (
            clr_curve[0][1] !== 0 && clr_curve[1][2] == 0 && clr_curve[2][2] == 0 && clr_curve[3][2] == 0 && clr_curve[4][2] == 0 && clr_curve[5][2] == 0
          );

          resolve();
        }).catch(console.error);
      });
    },
    paginate: function(array, page_size, page_number) {
      return array.slice(page_number * page_size, page_number * page_size + page_size);
    },
    tabChange: function(input) {

      console.log(input);
      window.location = `${this.grant.details_url}?tab=${input}`;
    },
    enableTab: function() {
      let vm = this;
      let urlParams = new URLSearchParams(window.location.search);

      vm.tab = urlParams.get('tab');

      switch (vm.tab) {
        case 'sybil_profile':
          vm.tabSelected = 4;
          break;
        case 'stats':
          vm.tabSelected = 3;
          break;
        default:
          vm.tabSelected = 0;
      }
      window.history.replaceState({}, document.title, `${window.location.pathname}`);
    },
    fetchRelated: function() {
      const vm = this;
      const size = 3;
      let ids;

      if (!Object.keys(vm.grant.metadata).length || !vm.grant.metadata?.related?.length) {
        return;
      }

      ids = vm.grant.metadata.related.map(arr => {
        return arr[0];
      });

      vm.relatedGrantsIds = vm.paginate(ids, size, vm.relatedGrantsPage);

      vm.relatedGrantsPage += 1;

      vm.relatedGrantsHasNext = vm.relatedGrantsPage + 1 < ids.length / size;

      if (!vm.relatedGrantsIds.length) {
        return;
      }

      vm.loadingRelated = true;

      const url = `/grants/v1/api/grants?pks=${vm.relatedGrantsIds}`;

      fetch(url).then(function(res) {
        return res.json();
      }).then(function(json) {
        json.grants.forEach(function(item) {
          vm.relatedGrants.push(item);
        });
        vm.loadingRelated = false;
      }).catch(console.error);
    },
    fetchTransactions: function() {
      const vm = this;

      page = vm.transactions.next_page_number;
      if (!page) {
        return;
      }
      vm.loadingTx = true;

      const url = `/grants/v1/api/grant/${vm.grant.id}/contributions?page=${page}`;

      fetch(url).then(function(res) {
        return res.json();
      }).then(function(json) {
        json.contributions.forEach(function(item) {
          vm.transactions.grantTransactions.push(item);
        });

        vm.transactions.num_pages = json.num_pages;
        vm.transactions.has_next = json.has_next;
        vm.transactions.next_page_number = json.next_page_number;
        vm.transactions.count = json.count;
        vm.loadingTx = false;

      }).catch(console.error);
    },
    scrollToElement(element) {
      const container = this.$refs[element];

      container.scrollIntoViewIfNeeded({behavior: 'smooth', block: 'start'});
    },
    closeGrantCreatedNotification: function() {
      let vm = this;

      vm.modalShow = false;
      delete localStorage['grant_state'];
    }
  }
});

if (document.getElementById('gc-grant-detail')) {
  appGrantDetails = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grant-detail',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        modalShow: localStorage['grant_state'] == 'created',
        loading: false,
        loadingTx: false,
        loadingRelated: false,
        relatedGrants: [],
        relatedGrantsPage: 0,
        relatedGrantsHasNext: false,
        relatedGrantsIds: [],
        transactions: {
          grantTransactions: [],
          next_page_number: 1
        },
        isStaff: isStaff,
        grant: {},
        tabSelected: 0,
        tab: null
      };
    },
    mounted: function() {
      this.enableTab();
      this.fetchGrantDetails();
    }
  });
}
