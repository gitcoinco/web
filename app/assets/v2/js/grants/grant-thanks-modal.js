Vue.component('contribution-thanks-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      modalId: 'contribution-thanks',
      numberOfContributions: 0,
      donations: [],
      tweetUrl: ''
    };
  },
  mounted: function() {
    const shouldShow = Boolean(localStorage.getItem('contributions_were_successful'));

    this.numberOfContributions = Number(localStorage.getItem('contributions_count'));

    this.tweetUrl = `https://twitter.com/intent/tweet?text=I just funded ${this.numberOfContributions} grants on @gitcoin ${CartData.share_url()}`;

    if (shouldShow) {
      this.$bvModal.show(this.modalId);
    }

    this.donations = CartData.loadCart();
  },
  methods: {
    close() {
      this.$bvModal.hide(this.modalId);
    },
    handleHide() {
      localStorage.removeItem('contributions_were_successful');
      localStorage.removeItem('contributions_count');
      CartData.setCart([]);
    },
    showSaveAsCollection() {
      this.$bvModal.show('create-collection');
    }
  }
});
