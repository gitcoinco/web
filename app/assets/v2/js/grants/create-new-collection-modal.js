Vue.component('create-new-collection-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      modalId: 'create-new-collection',
      collectionTitle: '',
      collectionDescription: '',
      showCreateCollection: false
    };
  },
  computed: {
    isValidCollection() {
      if (this.collectionTitle.length > 3 && this.collectionDescription.length < 140) {
        return true;
      }

      return false;
    }
  },
  methods: {
    show() {
      this.showCreateCollection = true;
    },
    close() {
      this.$bvModal.hide(this.modalId);
    },
    createCollection: async function() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      let response;

      const body = {
        collectionTitle: this.collectionTitle,
        collectionDescription: this.collectionDescription
      };

      try {
        // post
        response = await fetchData('/grants/v1/api/collections/new', 'POST', body, {'X-CSRFToken': csrfmiddlewaretoken});
        const redirect = `/grants/explorer/?collection_id=${response.collection.id}`;
        // success

        _alert('Congratulations, your new collection was created successfully!', 'success');
        // clean
        this.cleanCollectionModal();
        // hide
        this.$bvModal.hide(this.modalId);
        // allow the user to read the alert message before redirecting
        setTimeout(() => {
          window.location = redirect;
        }, 2000);
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
