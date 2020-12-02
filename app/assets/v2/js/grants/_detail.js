
Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);
Quill.register('modules/ImageExtend', ImageExtend);


Vue.mixin({
  methods: {
    fetchGrantDetails: function(id) {
      let vm = this;

      vm.loading = true;
      if (!id) {
        id = grantDetails.grant_id;
      }

      let url = `/grants/v1/api/grant/${id}/`;

      return new Promise(resolve => {

        fetch(url).then(function(res) {
          return res.json();
        }).then(function(json) {
          vm.grant = json.grants;
          vm.loading = false;
          if (vm.tab) {
            setTimeout(function() {
              vm.scrollToElement('grant-tabs');
            }, 1000);
          }

          resolve();
        }).catch(console.error);
      });


    },
    fetchRelated: function() {
      let vm = this;
      let ids;

      if (!Object.keys(vm.grant.metadata).length || !vm.grant.metadata?.related?.length || vm.relatedGrants.length) {
        return;
      }

      ids = vm.grant.metadata.related.map(arr => {
        return arr[0];
      });
      idsString = String(ids);

      let url = `/grants/v1/api/grants?pks=${idsString}`;

      fetch(url).then(function(res) {
        return res.json();
      }).then(function(json) {
        vm.relatedGrants = json.grants;

      }).catch(console.error);
    },
    fetchTransactions: function() {
      let vm = this;

      page = vm.transactions.next_page_number;
      vm.loadingTx = true;

      let url = `/grants/v1/api/grant/${vm.grant.id}/contributions?page=${page}`;

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
    backNavigation: function() {
      let vm = this;
      var lgi = localStorage.getItem('last_grants_index');
      var lgt = localStorage.getItem('last_grants_title');

      if (lgi && lgt) {
        vm.$set(vm.backLink, 'url', lgi);
        vm.$set(vm.backLink, 'title', lgt);
      }
    },
    tabChange: function(input) {

      console.log(input)
      window.location = `${this.grant.details_url}?tab=${input}`;
    },
    enableTab: function() {
      let vm = this;
      let urlParams = new URLSearchParams(window.location.search)

      vm.tab = urlParams.get('tab');

      switch (vm.tab) {
        case 'sybil_profile':
          vm.tabSelected =  4;
          break;
        case 'contributors':
          vm.tabSelected =  3;
          break;
        case 'stats':
          vm.tabSelected =  5;
          break;
        default:
          vm.tabSelected =  0;
      }
      window.history.replaceState({}, document.title, `${window.location.pathname}`);
    },
    scrollToElement(element) {
      let container = this.$refs[element];

      container.scrollIntoViewIfNeeded({behavior: "smooth", block: "start"});
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
        loadingTx: false,
        loading: false,
        isStaff: isStaff,
        transactions:{
          grantTransactions: [],
          next_page_number: 1
        },
        grant: {},
        tabSelected: 0,
        tab: null,
        relatedGrants: [],
        backLink: {
          url: '/grants',
          title: 'Grants'
        }
      };
    },
    mounted: function() {
      this.enableTab();
      this.backNavigation();
      this.fetchGrantDetails();
    }
  });
}
