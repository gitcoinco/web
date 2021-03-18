
Vue.component('contribution-trust-bonus', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      modalId: 'trust-bonus'
    };
  },
  methods: {
    show() {
      this.$bvModal.show(this.modalId);
    },
    close() {
      this.$bvModal.hide(this.modalId);
    },
    openProfileTrustBonus() {
      document.location = '/profile/trust';
    }
  }
});
