Vue.component('historical-claim', {
  delimiters: [ '[[', ']]' ],
  props: ['match'],
  computed: {
    payoutToken() {
      return this.match.grant_payout.token.symbol;
    }
  }
});
