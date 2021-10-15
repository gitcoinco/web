Vue.component('create-new-collection-modal', {
  delimiters: [ '[[', ']]' ],
  props: ['redirect'],
  data: function() {
    return {
      modalId: 'create-new-collection',
      collectionTitle: '',
      collectionDescription: '',
      showCreateCollection: false,
      collections: document.collections
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
      // catch any network failures...
      try {
        // pull csrf token
        const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        // wrap the content
        const body = {
          collectionTitle: this.collectionTitle,
          collectionDescription: this.collectionDescription
        };
        // post to create the new collection
        const response = await fetchData('/grants/v1/api/collections/new', 'POST', body, {'X-CSRFToken': csrfmiddlewaretoken});

        // toast the success
        _alert('Congratulations, your new collection was created successfully!', 'success', 3000);
        // clean the state
        this.cleanCollectionModal();
        // hide the modal
        this.$bvModal.hide(this.modalId);
        // record the new collection
        this.collections.push({
          id: response.collection.id,
          title: body.collectionTitle
        });
        // allow the user to read the alert message before (optionally) redirecting
        if (this.redirect) {
          setTimeout(() => {
            window.location = `/grants/explorer/?collection_id=${response.collection.id}`;
          }, 2000);
        }
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
