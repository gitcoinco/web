Vue.component('contribution-thanks-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      modalId: 'contribution-thanks',
      numberOfContributions: 0,
      donations: [],
      tweetUrl: '',
      current_type: 'collections',
      hideCollectionButtons: true,
      collection: {
        id: 0,
        title: '',
        description: '',
        grants: [],
        hideButtons: true,
        owner: {
          url: document.contxt.profile_url,
          handle: document.contxt.github_handle,
          avatar_url: '/dynamic/avatar/' + document.contxt.github_handle
        }
      }
    };
  },
  mounted: function() {
    const checkoutData = CartData.loadCheckedOut();
    const shouldShow = checkoutData.length > 0;

    this.numberOfContributions = checkoutData.length;

    this.tweetUrl = `https://twitter.com/intent/tweet?text=I just funded ${this.numberOfContributions} grants on @gitcoin ${CartData.share_url()}`;

    if (shouldShow) {
      this.$bvModal.show(this.modalId);
    }

    this.donations = checkoutData;

    this.collection.count = checkoutData.length;

    this.collection.grants = checkoutData.map((grant) => {

      return {...grant, logo: grant.grant_logo }
    });
  },
  methods: {
    showSingleCollection() {
      return true;
    },
    close() {
      this.$bvModal.hide(this.modalId);
    },
    handleHide() {
      CartData.clearCheckedOut();
    },
    showSaveAsCollection() {
      this.$bvModal.show('create-collection');
    }
  }
});
