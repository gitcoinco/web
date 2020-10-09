Vue.component('grant-card', {
  delimiters: [ '[[', ']]' ],
  props: [ 'grant', 'cred', 'token', 'view', 'short', 'show_contributions',
    'contributions', 'toggle_following', 'collection', 'has_collections'
  ],
  data: function() {
    return {
      collections: document.collections,
      currentUser: document.contxt.github_handle,
      isCurator: false
    };
  },
  methods: {
    checkIsCurator: function() {
      if (this.currentUser && this.collection && this.collection.curators.length) {
        const curators = this.collection.curators.map(collection => collection.handle);

        this.isCurator = curators.indexOf(this.currentUser) !== -1;
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
      const grantCartPayloadURL = `v1/api/${grant.id}/cart_payload`;
      const response = await fetchData(grantCartPayloadURL, 'GET');

      CartData.addToCart(response.grant);

      showSideCart();
    },
    addToCollection: async function({collection, grant}) {
      const collectionAddGrantURL = `v1/api/collections/${collection.id}/grants/add`;
      const response = await fetchData(collectionAddGrantURL, 'POST', {
        'grant': grant.id
      });

      _alert('Grant added successfully', 'success', 1000);
    }
  },
  mounted() {
    this.checkIsCurator();
  }
});

Vue.component('grant-collection', {
  delimiters: [ '[[', ']]' ],
  props: ['collection'],
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
      const collectionDetailsURL = `v1/api/collections/${this.collection.id}`;
      const collection = await fetchData(collectionDetailsURL, 'GET');

      (collection.grants || []).forEach((grant) => {
        CartData.addToCart(grant);
      });

      showSideCart();
    },
    getGrantLogo(index) {
      return this.collection.grants[index].logo;
    }
  }
});
