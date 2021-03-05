
Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);
Quill.register('modules/ImageExtend', ImageExtend);


Vue.mixin({
  methods: {
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
          vm.grant = json.grants;
          vm.loading = false;
          // if (vm.tab) {
          //   setTimeout(function() {
          //     vm.scrollToElement('grant-tabs');
          //   }, 1000);
          // }

          resolve();
        }).catch(console.error);
      });
    },
    backNavigation: function() {
      const vm = this;
      const lgi = localStorage.getItem('last_grants_index');
      const lgt = localStorage.getItem('last_grants_title');

      if (lgi && lgt) {
        vm.$set(vm.backLink, 'url', lgi);
        vm.$set(vm.backLink, 'title', lgt);
      }
    },
    scrollToElement(element) {
      const container = this.$refs[element];

      container.scrollIntoViewIfNeeded({behavior: 'smooth', block: 'start'});
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
        loading: false,
        isStaff: isStaff,
        grant: {},
        tabSelected: 0,
        tab: null,
        backLink: {
          url: '/grants',
          title: 'Grants'
        }
      };
    },
    mounted: function() {
      this.backNavigation();
      this.fetchGrantDetails();
    }
  });
}
