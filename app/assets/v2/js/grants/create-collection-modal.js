Vue.component('create-collection-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      modalId: 'create-collection',
      collectionTitle: '',
      collectionDescription: '',
      collections: [],
      grantIds: [],
      imgURL: '',
      selectedCollection: null,
      showCreateCollection: false
    };
  },
  mounted: function() {
    const checkedOut = CartData.loadCheckedOut();
    const cart = (checkedOut.length > 0 ? checkedOut : CartData.loadCart());

    this.grantIds = cart.map(grant => grant.grant_id).join(',');

    this.imgURL = '/dynamic/grants_cart_thumb/' + document.contxt['github_handle'] + '/' + this.grantIds.join(',');
  },
  computed: {
    isValidCollection() {
      if (this.selectedCollection !== null) {
        return true;
      } else if (this.collectionTitle.length > 3 && this.collectionDescription.length < 140) {
        return true;
      }

      return false;
    }
  },
  methods: {
    fetchCollections() {
      this.showCreateCollection = true;
      fetchData('/grants/v1/api/collections/').then(response => {
        if (response.collections && response.collections.length > 0) {
          this.collections = response.collections;
        }
      });
    },
    close() {
      this.$bvModal.hide(this.modalId);
    },
    createCollection: async function() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      let response;

      const body = {
        collectionTitle: this.collectionTitle,
        collectionDescription: this.collectionDescription,
        grants: this.grantIds
      };

      if (this.selectedCollection) {
        body['collection'] = this.selectedCollection;
      }

      try {

        response = await fetchData('/grants/v1/api/collections/new', 'POST', body, {'X-CSRFToken': csrfmiddlewaretoken});
        const redirect = `/grants/explorer/?collection_id=${response.collection.id}`;

        _alert('Congratulations, your new collection was created successfully!', 'success');

        this.cleanCollectionModal();

        this.$bvModal.hide(this.modalId);
        this.$bvModal.hide('contribution-thanks'); // triggers cart clear

        window.open(redirect, '_blank');
      } catch (e) {
        _alert(e.msg, 'danger');
      }
    },
    cleanCollectionModal: function() {
      this.collectionTitle = '';
      this.collectionDescription = '';
    }
  }
});
