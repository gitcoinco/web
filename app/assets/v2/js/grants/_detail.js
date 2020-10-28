Vue.component('v-select', VueSelect.VueSelect);

Vue.mixin({
  methods: {
    fetchGrantDetails: function(id) {
      let vm = this;

      if (!id) {
        id = grantDetails.grant_id;
      }

      let url = `/grants/v1/api/grant/${id}/`;
      // var getdata = fetchData (url, 'GET');

      // $.when(getdata).then(function(response) {
      //   vm.grant = response.grants;
      // })
      return new Promise(resolve => {

        fetch(url).then(function(res)  {
          return res.json();


        }).then(function(json) {
          vm.grant = json.grants
          resolve()
        }).catch(console.error)
      })


    }
  },

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
        grant: {}

      };
    },
    mounted: function() {
      console.log('mount')

     this.fetchGrantDetails();

    },
  });
}


