Vue.component('delete-collection-modal', {
  delimiters: [ '[[', ']]' ],
  props: ['selectedCollection'],
  data: function() {
    return {
      modalId: 'delete-collection',
      showDeleteCollection: false
    };
  },
  methods: {
    show() {
      this.showDeleteCollection = true;
    },
    close() {
      this.$bvModal.hide(this.modalId);
    },
    deleteCollection: async function() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      let response;

      const body = {};

      if (this.$attrs.selected_collection) {
        body['collection'] = this.$attrs.selected_collection;
      }

      try {
        response = await fetchData('/grants/v1/api/collections/delete', 'POST', body, {'X-CSRFToken': csrfmiddlewaretoken});
        const redirect = '/grants/explorer/';

        _alert('Congratulations, your collection was deleted successfully!', 'success');

        this.$bvModal.hide(this.modalId);

        // allow the user to read the alert message before redirecting
        setTimeout(() => {
          window.location = redirect;
        }, 2000);
      } catch (e) {
        _alert(e.msg, 'danger');
      }
    }
  }
});
