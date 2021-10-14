Vue.component('grant-card', {
  delimiters: [ '[[', ']]' ],
  props: [ 'grant', 'cred', 'token', 'view', 'short', 'show_contributions',
    'contributions', 'toggle_following', 'collection', 'editing_collection'
  ],
  data: function() {
    return {
      collections: document.collections,
      currentUser: document.contxt.github_handle,
      isCurator: false,
      selectedCollection: null
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
    addToThisCollection: function() {
      const collection_grant_ids = [ ...this.$attrs.collection_grant_ids, this.grant.id ];

      this.$emit('update:collection_grant_ids', collection_grant_ids);
    },
    removeFromThisCollection: function() {
      const collection_grant_ids = this.$attrs.collection_grant_ids.filter((grantId) => grantId != this.grant.id);

      this.$emit('update:collection_grant_ids', collection_grant_ids);
    },
    addToCollection: async function(collection, grant) {
      const collectionAddGrantURL = `/grants/v1/api/collections/${collection.id}/grants/add`;
      const response = await fetchData(collectionAddGrantURL, 'POST', {
        'grant': grant.id
      });

      _alert('Grant added successfully', 'success', 1000);
    },
    showModal: function(modalId) {
      this.selectedCollection = this.collections[0] && this.collections[0].id;
      this.$bvModal.show(modalId);
    },
    closeModal: function(modalId) {
      this.$bvModal.hide(modalId);
    },
    addGrantToSelectedCollection: async function() {
      const collection = this.collections.find(collection => collection.id == this.selectedCollection);

      await this.addToCollection(collection, this.grant);

      this.closeModal('add-to-collection');
    }
  },
  computed: {
    has_collections() {
      return this.collections.length;
    },
    isUserLogged() {
      let vm = this;

      if (document.contxt.github_handle) {
        return true;
      }
    },
    isInCollection() {
      if (this.$attrs.collection_grant_ids && this.$attrs.collection_grant_ids.indexOf(this.grant.id) !== -1) {
        return true;
      }

      return false;
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
  props: [ 'collection', 'activeCollection' ],
  methods: {
    shareCollection: function() {
      let share_url = document.querySelector(`#collection-${this.collection.id}`);

      share_url.setAttribute('type', 'text');
      share_url.select();

      try {
        const successful = document.execCommand('copy');
        const msg = successful ? 'successfully' : 'unsuccessfully';

        _alert(`Grant collection was copied ${msg}: ${share_url.value}`, 'success', 3000);
      } catch (err) {
        _alert('Oops, unable to copy', 'danger');
      }

      /* unselect the range */
      share_url.setAttribute('type', 'hidden');
      window.getSelection().removeAllRanges();
    },
    tweetCollection: function() {
      let share_url = document.querySelector(`#collection-${this.collection.id}`);
      let tweetUrl = `https://twitter.com/intent/tweet?text=Check out this Grant Collection on @gitcoin ${share_url.value}`;

      window.open(tweetUrl, '_blank');
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
    },
    getGrantTitle(index) {
      return `${this.collection.cache?.grants[index]?.title}`;
    }
  }
});
