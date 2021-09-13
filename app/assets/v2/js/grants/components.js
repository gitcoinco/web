Vue.component('grant-card', {
  delimiters: [ '[[', ']]' ],
  props: [ 'grant', 'cred', 'token', 'view', 'short', 'show_contributions',
    'contributions', 'toggle_following', 'collection'
  ],
  data: function() {
    return {
      collections: document.collections,
      currentUser: document.contxt.github_handle,
      isCurator: false
    };
  },
  methods: {
    quickView: function(event) {
      event.preventDefault();
      let vm = this;

      appGrants.grant = vm.grant;
      appGrants.$refs['sidebar-quick-view'].$on('hidden', function(e) {
        appGrants.grant = {};
      });
      vm.$root.$emit('bv::toggle::collapse', 'sidebar-quick-view');
    },
    grantInCart: function() {
      let vm = this;
      let inCart = CartData.cartContainsGrantWithId(vm.grant.id);

      vm.$set(vm.grant, 'isInCart', inCart);
      return vm.grant.isInCart;
    },
    checkIsCurator: function() {
      let vm = this;
      let currentUser;

      // Validate the user presence and clean current user handle
      if (vm.currentUser) {
        currentUser = vm.currentUser.replace(/@/, '').replace(/\s/g, '');
      } else {
        return;
      }

      // Validate if exists the collection
      if (this.collection && this.collection.curators.length) {
        this.collection.curators.map(curator => {
          let currentCurator;

          // Clean curator handle
          if (curator && curator.handle) {
            currentCurator = curator.handle.replace(/@/, '').replace(/\s/g, '');
          }

          if (currentCurator === currentUser) {
            vm.isCurator = true;
          }
        });
      }
    },
    get_clr_prediction: function(indexA, indexB) {
      if (this.grant.clr_prediction_curve && this.grant.clr_prediction_curve.length) {
        return this.grant.clr_prediction_curve[indexA][indexB];
      }
    },
    getContributions: function(grantId) {
      return this.contributions[grantId] || [];
    },
    toggleFollowingGrant: async function(grantId, event) {
      event.preventDefault();

      const favorite_url = `/grants/${grantId}/favorite`;
      let response = await fetchData(favorite_url, 'POST');

      if (response.action === 'follow') {
        this.grant.favorite = true;
      } else {
        this.grant.favorite = false;
      }

      return true;
    },
    addToCart: async function(grant) {
      let vm = this;
      const grantCartPayloadURL = `/grants/v1/api/${grant.id}/cart_payload`;
      const response = await fetchData(grantCartPayloadURL, 'GET');

      vm.$set(vm.grant, 'isInCart', true);
      CartData.addToCart(response.grant);
    },
    removeFromCart: function() {
      let vm = this;

      vm.$set(vm.grant, 'isInCart', false);
      CartData.removeIdFromCart(vm.grant.id);
    },
    addToCollection: async function(collection, grant) {
      const collectionAddGrantURL = `/grants/v1/api/collections/${collection.id}/grants/add`;
      const response = await fetchData(collectionAddGrantURL, 'POST', {
        'grant': grant.id
      });

      _alert('Grant added successfully', 'success', 1000);
    }
  },
  computed: {
    has_collections() {
      return this.collections.length;
    }

  },
  mounted() {
    this.checkIsCurator();
    this.grantInCart();
  }
});

Vue.component('grant-collection', {
  template: '#grant-collection',
  delimiters: [ '[[', ']]' ],
  props: [ 'collection', 'small', 'activeCollection' ],
  methods: {
    shareCollection: function() {
      let testingCodeToCopy = document.querySelector(`#collection-${this.collection.id}`);

      testingCodeToCopy.setAttribute('type', 'text');
      testingCodeToCopy.select();

      try {
        const successful = document.execCommand('copy');
        const msg = successful ? 'successful' : 'unsuccessful';

        alert(`Grant collection was copied ${msg}: ${testingCodeToCopy.value}`);
      } catch (err) {
        alert('Oops, unable to copy');
      }

      /* unselect the range */
      testingCodeToCopy.setAttribute('type', 'hidden');
      window.getSelection().removeAllRanges();
    },
    addToCart: async function() {
      const collectionDetailsURL = `/grants/v1/api/collections/${this.collection.id}`;
      const collection = await fetchData(collectionDetailsURL, 'GET');

      (collection.grants || []).forEach((grant) => {
        CartData.addToCart(grant);
      });
    },
    getGrantLogo(index) {
      return `${this.collection.cache?.grants[index]?.logo}`;
    }
  }
});
