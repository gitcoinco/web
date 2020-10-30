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
          vm.grantInCart();
          resolve()
        }).catch(console.error)
      })


    },
    fetchRelated: function(ids) {
      let vm = this;

      let url = `http://localhost:8000/grants/v1/api/grants?pks=${ids}`
      vm.relatedGrants
    },
    grantInCart: function() {
      let vm = this;
      let inCart = CartData.cartContainsGrantWithId(vm.grant.id);
      console.log(inCart, vm.grant.id)

      vm.$set(vm.grant, 'isInCart', inCart);
      return vm.grant.isInCart;
    },
    addToCart: async function() {
      let vm = this;
      const grantCartPayloadURL = `/grants/v1/api/${vm.grant.id}/cart_payload`;
      const response = await fetchData(grantCartPayloadURL, 'GET');

      vm.$set(vm.grant, 'isInCart', true);
      CartData.addToCart(response.grant);
    },
    removeFromCart: function() {
      let vm = this;
      console.log('removeFromCart')
      vm.$set(vm.grant, 'isInCart', false);
      CartData.removeIdFromCart(vm.grant.id);
    },
  },
  computed: {

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
        grant: {},
        relatedGrants: []

      };
    },
    mounted: function() {
      console.log('mount')

     this.fetchGrantDetails();

    },
  });
}


