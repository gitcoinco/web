


Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);
Quill.register('modules/ImageExtend', ImageExtend);


Vue.mixin({
  methods: {
    fetchGrantDetails: function(id) {
      let vm = this;

      if (!id) {
        id = grantDetails.grant_id;
      }

      let url = `/grants/v1/api/grant/${id}/`;

      return new Promise(resolve => {

        fetch(url).then(function(res) {
          return res.json();
        }).then(function(json) {
          vm.grant = json.grants;
          resolve();
        }).catch(console.error);
      });


    },
    fetchRelated: function() {
      let vm = this;
      let ids;

      if (!vm.grant.metadata.related.length || vm.relatedGrants.length) {
        return;
      }

      ids = vm.grant.metadata.related.map(arr => {
        return arr[0];
      });
      idsString = String(ids);

      let url = `http://localhost:8000/grants/v1/api/grants?pks=${idsString}`;

      fetch(url).then(function(res) {
        return res.json();
      }).then(function(json) {
        vm.relatedGrants = json.grants;

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
        grant: {},
        relatedGrants: [],
        backLink:{
          url: '/grants',
          title: 'Grants'
        }
      };
    },
    mounted: function() {
      this.backNavigation()
      this.fetchGrantDetails();
    }
  });
}


