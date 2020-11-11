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

          // if (vm.grant.metadata.related[0].length) {
          //   vm.fetchRelated(String(vm.grant.metadata.related[0]))
          // }

          resolve()
        }).catch(console.error)
      })


    },
    fetchRelated: function() {
      let vm = this;
      let ids;

      if (!vm.grant.metadata.related.length || vm.relatedGrants.length) {
        return;
      }

      ids = vm.grant.metadata.related.map(arr => {return arr[0];});
      idsString = String(ids);

      let url = `http://localhost:8000/grants/v1/api/grants?pks=${idsString}`
      fetch(url).then(function(res)  {
        return res.json();
      }).then(function(json) {
        vm.relatedGrants = json.grants;

      }).catch(console.error)
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
    toggleFollowingGrant: async function(grantId) {
      let vm = this;

      const favoriteUrl = `/grants/${grantId}/favorite`;
      let response = await fetchData(favoriteUrl, 'POST');

      if (response.action === 'follow') {
        vm.grant.favorite = true;
      } else {
        vm.grant.favorite = false;
      }

      return true;
    },
    flag: function() {
      let vm = this;


      const comment = prompt('What is your reason for flagging this Grant?');

      if (!comment) {
        return;
      }

      if (!document.contxt.github_handle) {
        _alert({ message: gettext('Please login.') }, 'error', 1000);
        return;
      }

      const data = {
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        'comment': comment
      };

      $.ajax({
        type: 'post',
        url: `/grants/flag/${vm.grant.id}`,
        data,
        success: function(json) {
          _alert({ message: gettext('Your flag has been sent to Gitcoin.') }, 'success', 1000);
        },
        error: function() {
          _alert({ message: gettext('Your report failed to save Please try again.') }, 'error', 1000);
        }
      });
    }
  },
  computed: {
    filteredMsg: function() {
      let msgs = [
        '💪 keep up the great work',
        '👍 i appreciate you',
        '🙌 Great Job',
        '😍 love the mission of your project'
      ]
      if (!this.grant?.metadata?.wall_of_love) {
        return;
      }
      console.log(Object.keys(this.grant.metadata).length > 0 )
      console.log(msgs)
      return this.grant?.metadata?.wall_of_love.filter((msg) => {
        if(msgs.includes(msg[0])) {
          return msg;
        }
      });
    },
    itemsForList() {
      if (this.grant.metadata && !Object.keys(this.grant.metadata).length) {
        return
      }
      this.rows = this.grant?.metadata?.wall_of_love.length || 0;
      return this.grant?.metadata?.wall_of_love.slice(
        (this.currentPage - 1) * this.perPage,
        this.currentPage * this.perPage,
      );
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
        grant: {},
        relatedGrants: [],
        rows: 0,
        perPage: 4,
        currentPage: 1

      };
    },
    mounted: function() {
      console.log('mount')

     this.fetchGrantDetails();

    },
  });
}


